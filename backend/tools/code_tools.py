import os
import subprocess
import logging
import PyPDF2 # type: ignore

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