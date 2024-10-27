import base64
import os
import requests
import logging
from pathlib import Path
from typing import Union, List, Dict, Optional, Literal
import mimetypes
from openai import OpenAI
from urllib.parse import urlparse
from typing import Union, List, Dict, Optional, Literal

client = OpenAI()

def analyze_image(
    image_source: Union[str, List[str]],
    prompt: str = "What's in this image?",
    detail: Literal["auto", "low", "high"] = "auto",
    model: str = "gpt-4o",
    max_tokens: int = 1000
) -> Dict[str, Union[str, Dict[str, int]]]:
    """
    Analyze one or more images using OpenAI's Vision API.
    """
    analyzer = ImageAnalyzer()
    return analyzer.analyze_image(image_source, prompt, detail, model, max_tokens)

class ImageAnalyzer:
    """
    A class for analyzing images using OpenAI's Vision API.

    This class provides methods to analyze both local and remote images using
    OpenAI's GPT-4o model, capable of image analysis. It supports multiple image formats and can
    handle both single and multiple image analysis.

    Attributes:
        supported_formats (set): Set of supported image file extensions
        client (OpenAI): OpenAI client instance

    Raises:
        ValueError: If an invalid API key or unsupported image format is provided
        FileNotFoundError: If a local image file cannot be found
        requests.exceptions.RequestException: If there's an error downloading an image
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the ImageAnalyzer with OpenAI API credentials.

        Args:
            api_key (Optional[str]): OpenAI API key. If None, will use OPENAI_API_KEY
                environment variable.

        Raises:
            ValueError: If neither api_key parameter nor OPENAI_API_KEY environment
                variable is set
        """
        self.client = OpenAI(api_key=api_key)
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.webp'}

    def _encode_image(self, image_path: str) -> str:
        """
        Encode a local image file to base64 string.

        Args:
            image_path (str): Path to the local image file

        Returns:
            str: Base64 encoded string of the image

        Raises:
            FileNotFoundError: If the image file doesn't exist
            IOError: If there's an error reading the file
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _validate_image_format(self, file_path: str) -> bool:
        """
        Validate if the image format is supported.

        Args:
            file_path (str): Path to the image file or URL

        Returns:
            bool: True if the format is supported, False otherwise
        """
        extension = Path(file_path).suffix.lower()
        return extension in self.supported_formats

    def _download_image(self, url: str, temp_path: str = "temp_image") -> str:
        """
        Download an image from a URL and save it to a temporary file.

        Args:
            url (str): URL of the image to download
            temp_path (str): Base path for the temporary file

        Returns:
            str: Path to the downloaded temporary file

        Raises:
            requests.exceptions.RequestException: If there's an error downloading the image
            ValueError: If the image format is not supported
        """
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type')
        extension = mimetypes.guess_extension(content_type) if content_type else Path(urlparse(url).path).suffix
        
        if not extension or extension.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported image format: {extension}")
            
        temp_file = f"{temp_path}{extension}"
        with open(temp_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return temp_file

    def analyze_image(
        self,
        image_source: Union[str, List[str]],
        prompt: str = "What's in this image?",
        detail: Literal["auto", "low", "high"] = "auto",
        model: str = "gpt-4o",
        max_tokens: int = 300
    ) -> Dict[str, Union[str, Dict[str, int]]]:
        """
        Analyze one or more images using OpenAI's Vision API.

        This method can process both local image files and images from URLs. It supports
        multiple image formats (PNG, JPG, JPEG, WebP) and can analyze multiple images
        in a single request.

        Args:
            image_source (Union[str, List[str]]): Single image path/URL or list of
                image paths/URLs to analyze. Supports both local files and HTTP(S) URLs.
            prompt (str, optional): Question or instruction for the model about the
                image(s). Defaults to "What's in this image?".
            detail (Literal["auto", "low", "high"], optional): Level of detail for
                analysis. Affects token usage and cost. Defaults to "auto".
                - "auto": Let the API choose based on image size
                - "low": Low resolution analysis (faster, cheaper)
                - "high": High resolution analysis (more detailed, more expensive)
            model (str, optional): OpenAI model to use for analysis.
                Defaults to "gpt-4o".
            max_tokens (int, optional): Maximum tokens for the response.
                Defaults to 300.

        Returns:
            Dict[str, Union[str, Dict[str, int]]]: Dictionary containing:
                - content (str): The model's analysis of the image(s)
                - usage (Dict[str, int]): Token usage statistics
                    - prompt_tokens (int): Tokens used in the prompt
                    - completion_tokens (int): Tokens used in the completion
                    - total_tokens (int): Total tokens used

        Raises:
            ValueError: If image format is unsupported or detail level is invalid
            FileNotFoundError: If a local image file cannot be found
            requests.exceptions.RequestException: If there's an error downloading an image
            openai.OpenAIError: If there's an error with the OpenAI API request

        Examples:
            # Analyze a local image
            analyzer = ImageAnalyzer()
            result = analyzer.analyze_image("path/to/image.jpg")
            print(result["content"])

            # Analyze an image from URL
            result = analyzer.analyze_image(
                "https://example.com/image.jpg",
                prompt="Describe the main objects in this image",
                detail="high"
            )

            # Analyze multiple images
            images = ["image1.jpg", "https://example.com/image2.jpg"]
            result = analyzer.analyze_image(
                image_source=images,
                prompt="Compare these images"
            )
        """
        if isinstance(image_source, str):
            image_source = [image_source]
            
        content = [{"type": "text", "text": prompt}]
        temp_files = []
        
        try:
            for source in image_source:
                is_url = urlparse(source).scheme in ('http', 'https')
                
                if is_url:
                    temp_file = self._download_image(source)
                    temp_files.append(temp_file)
                    image_path = temp_file
                else:
                    if not os.path.exists(source):
                        raise FileNotFoundError(f"Image file not found: {source}")
                    if not self._validate_image_format(source):
                        raise ValueError(f"Unsupported image format: {source}")
                    image_path = source
                
                base64_image = self._encode_image(image_path)
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": detail
                    }
                })
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": content}],
                max_tokens=max_tokens
            )
            
            return {
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        finally:
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except:
                    pass

def generate_image(
    prompt: str,
    size: Literal["1024x1024", "1792x1024", "1024x1792"] = "1024x1024",
    quality: Literal["standard", "hd"] = "hd",
    style: Literal["vivid", "natural"] = "vivid",
    model: str = "dall-e-3",
    n: int = 1,
    response_format: Literal["url", "b64_json"] = "url"
) -> dict:
    """
    Generate an image using DALL-E 3.
    
    Args:
        prompt (str): Text description of the desired image(s). Max 4000 characters.
        size (str): Image size - "1024x1024", "1792x1024", or "1024x1792". Defaults to "1024x1024".
        quality (str): Image quality - "standard" or "hd". Defaults to "hd".
        style (str): Image style - "vivid" or "natural". Defaults to "vivid".
        model (str): Model to use. Defaults to "dall-e-3".
        n (int): Number of images to generate. DALL-E 3 only supports n=1.
        response_format (str): Format for generated images - "url" or "b64_json". Defaults to "url".
    
    Returns:
        dict: Response from the OpenAI API containing image data
        
    Raises:
        Exception: If the API call fails
    """
    try:
        logging.info(f"Generating image with prompt: {prompt}")
        response = client.images.generate(
            model=model,
            prompt=prompt,
            n=n,
            size=size,
            quality=quality,
            style=style,
            response_format=response_format
        )
        logging.info("Image generated successfully")
        return {
            "url": response.data[0].url,
            "revised_prompt": getattr(response.data[0], 'revised_prompt', None)
        }
    except Exception as e:
        error_message = f"Error generating image: {str(e)}"
        logging.error(error_message)
        return {"error": error_message}