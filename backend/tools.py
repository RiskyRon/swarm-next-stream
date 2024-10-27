import os
import json
import sys
import venv
import subprocess
import PyPDF2 # type: ignore
import trafilatura # type: ignore
import logging
from openai import OpenAI
from typing import List, Dict, Generator, Any
from bs4 import BeautifulSoup # type: ignore
from tavily import TavilyClient # type: ignore
from urllib.parse import urljoin, urlparse
from youtube_transcript_api import YouTubeTranscriptApi # type: ignore
from gpt_researcher import GPTResearcher # type: ignore
import asyncio
import nest_asyncio  # type: ignore # Add this import

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def tavily_search(query: str) -> str:
    """
    Perform a search using the Tavily API.

    This function takes a search query and uses the Tavily client to perform a basic search.
    It returns the search context limited to a maximum of 8000 tokens.

    Args:
        query (str): The search query string.

    Returns:
        str: The search result context or an error message if the search fails.
    """
    logging.info(f"Performing Tavily search with query: {query}")
    try:
        search_result = tavily_client.get_search_context(query, search_depth="basic", max_tokens=8000)
        logging.info("Tavily search completed successfully")
        return search_result
    except Exception as e:
        error_message = f"Error performing Tavily search: {str(e)}"
        logging.error(error_message)
        return error_message



async def fetch_report(query):
    """
    Fetch a research report based on the provided query and report type.
    """
    researcher = GPTResearcher(query=query)
    await researcher.conduct_research()
    report = await researcher.write_report()
    return report

def run_async(coroutine):
    """Helper function to run async functions in a sync context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)

def generate_research_report(query: str) -> str:
    """
    Synchronous function to generate a research report.
    Uses the current event loop if one exists, or creates a new one if needed.
    """
    async def _async_research():
        try:
            researcher = GPTResearcher(query=query)
            await researcher.conduct_research()
            return await researcher.write_report()
        except Exception as e:
            logging.error(f"Error in _async_research: {str(e)}")
            return f"Error conducting research: {str(e)}"

    try:
        # Get the current event loop
        loop = asyncio.get_running_loop()
        # Create a new task in the current loop
        return loop.run_until_complete(_async_research())
    except RuntimeError:
        # If no event loop is running, create a new one
        return asyncio.run(_async_research())
    except Exception as e:
        logging.error(f"Error in generate_research_report: {str(e)}")
        return f"Error generating research report: {str(e)}"

def get_video_transcript(video_id):
    """
    Retrieve the transcript of a YouTube video.

    This function takes a YouTube video ID and attempts to fetch its transcript
    using the YouTubeTranscriptApi.

    Args:
        video_id (str): The ID of the YouTube video.

    Returns:
        list or str: A list containing the transcript data if successful,
                     or an error message string if the retrieval fails.
    """
    logging.info(f"Fetching transcript for video ID: {video_id}")
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        logging.info("Video transcript fetched successfully")
        return transcript
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logging.error(error_message)
        return error_message
    
def get_website_text_content(url: str) -> str:
    """
    Fetches and extracts the main text content from a given URL.

    Args:
        url (str): The URL of the website to fetch content from.

    Returns:
        str: The extracted text content from the website.

    Raises:
        Any exceptions raised by trafilatura.fetch_url or trafilatura.extract.
    """
    logging.info(f"Fetching content from URL: {url}")
    downloaded = trafilatura.fetch_url(url)
    text = trafilatura.extract(downloaded)
    logging.info("Website content extracted successfully")
    return text

def save_to_md(text: str, filename: str) -> None:
    """
    Saves the given text content to a markdown file.

    Args:
        text (str): The text content to be saved.
        filename (str): The name of the file to save the content to.

    Returns:
        None

    Raises:
        IOError: If there's an issue writing to the file.
    """
    logging.info(f"Saving content to file: {filename}")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)
        logging.info(f"Content saved successfully to {filename}")
    except IOError as e:
        logging.error(f"Error saving content to file: {str(e)}")

def get_all_urls(base_url):
    """
    Process a given URL to find all connected URLs within the same domain.

    This function downloads the content of the base_url, extracts all links,
    filters for links within the same domain and removes duplicates.

    Args:
        base_url (str): The URL to process.

    Returns:
        list: A list of unique URLs connected to the base_url within the same domain.

    Raises:
        Exception: If there's an error during URL processing.
    """
    logging.info(f"Processing URL: {base_url}")
    connected_urls = []
    try:
        downloaded = trafilatura.fetch_url(base_url)
        if downloaded is None:
            logging.warning(f"Failed to download {base_url}")
            return []

        soup = BeautifulSoup(downloaded, 'lxml')
        
        for link in soup.find_all('a', href=True):
            url = urljoin(base_url, link['href'])
            if urlparse(url).netloc == urlparse(base_url).netloc:
                connected_urls.append(url)

        # Remove duplicates
        connected_urls = list(set(connected_urls))

    except Exception as e:
        logging.error(f"Error processing URL: {str(e)}")

    return connected_urls

# Code Agent tools

def execute_command(command):
    """
    Execute a shell command and return its output.

    This function runs a given shell command using subprocess and returns the command's
    standard output. If the command fails, it returns the error message. This function has many uses. For example, performing CRUD operations, running a script, or executing a system command, using webget or curl to download a file, etc.

    Args:
        command (str): The shell command to execute.

    Returns:
        str: The command's standard output if successful, or an error message if the command fails.
    """
    logging.info(f"Executing command: {command}")
    current_dir = os.getcwd()
    workspace_dir = os.path.join(current_dir, 'WORKSPACE')
    
    try:
        os.chdir(workspace_dir)
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logging.info("Command executed successfully")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_message = f"Command failed with error: {e.stderr.strip()}"
        logging.error(error_message)
        return error_message
    finally:
        os.chdir(current_dir)

def read_file(file_path):
    """
    Read the contents of various file types from the WORKSPACE directory.

    Supported file types: md, txt, pdf, mdx, py, ts, tsx, js, jsx, css, scss, html
    The function automatically looks for files in the WORKSPACE directory relative to the
    current working directory.

    Args:
        file_path (str): The path to the file to be read, relative to WORKSPACE directory.

    Returns:
        str: The contents of the file.

    Raises:
        ValueError: If the file type is not supported.
        IOError: If there's an issue reading the file.
    """
    logging.info(f"Reading file: {file_path}")
    
    # Get the current directory and construct the WORKSPACE path
    current_dir = os.getcwd()
    workspace_dir = os.path.join(current_dir, 'WORKSPACE')
    
    # Construct the full file path within WORKSPACE
    full_file_path = os.path.join(workspace_dir, file_path)
    
    file_extension = os.path.splitext(full_file_path)[1].lower()
    supported_extensions = ['.md', '.txt', '.pdf', '.mdx', '.py', '.ts', '.tsx', '.js', '.jsx', '.css', '.scss', '.html']
    
    if file_extension not in supported_extensions:
        raise ValueError(f"Unsupported file type: {file_extension}")
    
    try:
        if file_extension == '.pdf':
            with open(full_file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content = ""
                for page in pdf_reader.pages:
                    content += page.extract_text()
        else:
            with open(full_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        
        logging.info(f"File {full_file_path} read successfully")
        return content
    
    except IOError as e:
        logging.error(f"Error reading file {full_file_path}: {str(e)}")
        raise

def install_package(package_name):
    """
    Install a Python package in the /venv virtual environment.

    Args:
        package_name (str): The name of the package to install.

    Returns:
        str: The output of the installation command or an error message.
    """
    logging.info(f"Installing package: {package_name}")
    venv_path = "venv"
    pip_path = f"{venv_path}/bin/pip"
    
    if not os.path.exists(pip_path):
        error_message = f"Virtual environment not found at {venv_path}"
        logging.error(error_message)
        return error_message
    
    try:
        result = subprocess.run([pip_path, "install", package_name], 
                                check=True, 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                text=True)
        logging.info(f"Package {package_name} installed successfully")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_message = f"Failed to install package {package_name}: {e.stderr.strip()}"
        logging.error(error_message)
        return error_message

def run_python_script(filename):
    """
    Run a Python script using the Python interpreter from the /venv virtual environment.

    Args:
        filename (str): The name of the Python script to run.

    Returns:
        str: The output of the script or an error message.
    """
    logging.info(f"Running Python script: {filename}")
    venv_path = "/venv"
    python_path = f"{venv_path}/bin/python"
    
    if not os.path.exists(python_path):
        error_message = f"Virtual environment not found at {venv_path}"
        logging.error(error_message)
        return error_message
    
    try:
        result = subprocess.run([python_path, filename], 
                                check=True, 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                text=True)
        logging.info(f"Script {filename} executed successfully")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_message = f"Failed to run script {filename}: {e.stderr.strip()}"
        logging.error(error_message)
        return error_message




def reason_with_o1(
    messages: List[Dict[str, str]], 
    model: str = "gpt-4",
    client: OpenAI = None,
    **kwargs
) -> Generator[str, None, None]:
    """
    Stream chat completions from OpenAI API.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        model: OpenAI model to use (default: "gpt-4")
        client: Optional OpenAI client instance
        **kwargs: Additional parameters to pass to completion.create()
    
    Yields:
        Content chunks from the streaming response
        
    Example:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ]
        
        for chunk in stream_chat_completion(messages):
            print(chunk, end='', flush=True)
    """
    # Create new client if none provided
    if client is None:
        client = OpenAI()
    
    # Create streaming completion
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        **kwargs
    )
    
    # Yield content from chunks
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content