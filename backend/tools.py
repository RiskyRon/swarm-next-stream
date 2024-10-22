#tools.py
import os
import json
import sys
import venv
import subprocess
import trafilatura # type: ignore
import logging
from bs4 import BeautifulSoup # type: ignore
from tavily import TavilyClient # type: ignore
from urllib.parse import urljoin, urlparse
from youtube_transcript_api import YouTubeTranscriptApi # type: ignore

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
    standard output. If the command fails, it returns the error message. This function has many uses. For example, performing CRUD operations, running a script, or executing a system command, using webget or curl to download a file, ect.

    Args:
        command (str): The shell command to execute.

    Returns:
        str: The command's standard output if successful, or an error message if the command fails.
    """
    logging.info(f"Executing command: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logging.info("Command executed successfully")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_message = f"Command failed with error: {e.stderr.strip()}"
        logging.error(error_message)
        return error_message

def read_file(file_path):
    """
    Read the contents of various file types.

    Supported file types: md, txt, pdf, mdx, py, ts, tsx, js, jsx, css, scss, html

    Args:
        file_path (str): The path to the file to be read.

    Returns:
        str: The contents of the file.

    Raises:
        ValueError: If the file type is not supported.
        IOError: If there's an issue reading the file.
    """
    import os
    import PyPDF2

    logging.info(f"Reading file: {file_path}")
    
    file_extension = os.path.splitext(file_path)[1].lower()
    
    supported_extensions = ['.md', '.txt', '.pdf', '.mdx', '.py', '.ts', '.tsx', '.js', '.jsx', '.css', '.scss', '.html']
    
    if file_extension not in supported_extensions:
        raise ValueError(f"Unsupported file type: {file_extension}")
    
    try:
        if file_extension == '.pdf':
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content = ""
                for page in pdf_reader.pages:
                    content += page.extract_text()
        else:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        
        logging.info(f"File {file_path} read successfully")
        return content
    
    except IOError as e:
        logging.error(f"Error reading file {file_path}: {str(e)}")
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


