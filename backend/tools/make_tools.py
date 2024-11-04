# backend/tools/make_tools.py

import requests
import logging
from typing import Dict, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MakeResponse:
    success: bool
    content: Union[str, Dict[str, Any]]
    status_code: int
    thread_id: Optional[str] = None
    error: Optional[str] = None

class MakeWebhookHandler:
    def __init__(self):
        self.webhook_url = "https://hook.eu2.make.com/lh4bjyea77m4h8gkv3vqc7vvm0290vwu"
        self.thread_id_store: Dict[str, str] = {}
        self.logger = logging.getLogger(__name__)

    def send_message(self, message: str) -> MakeResponse:
        """
        Send a message to Make.com webhook and handle various response types.
        
        Args:
            message (str): Message to send to Make.com
            
        Returns:
            MakeResponse: Structured response containing status and content
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, image/*'
        }

        thread_id = self.thread_id_store.get("latest_thread_id")
        if thread_id:
            headers['thread_id'] = thread_id

        data = {"message": message}
        
        try:
            self.logger.debug(f"Sending request to webhook: {data}")
            
            response = requests.post(
                self.webhook_url,
                json=data,
                headers=headers,
                timeout=30
            )
            
            # Log response details
            self.logger.debug(f"Response status: {response.status_code}")
            self.logger.debug(f"Response headers: {response.headers}")
            
            # Check if response is an image URL
            content_type = response.headers.get('Content-Type', '')
            if 'image' in content_type or response.text.startswith('http') and any(ext in response.text.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif']):
                return MakeResponse(
                    success=True,
                    content={"type": "image", "url": response.text.strip()},
                    status_code=response.status_code,
                    thread_id=response.headers.get('thread_id')
                )
            
            # Try to parse as JSON
            try:
                response_data = response.json()
                thread_id = response_data.get('thread_id')
                if thread_id:
                    self.thread_id_store["latest_thread_id"] = thread_id
                
                return MakeResponse(
                    success=True,
                    content=response_data,
                    status_code=response.status_code,
                    thread_id=thread_id
                )
            except ValueError:
                # If not JSON, return text response
                return MakeResponse(
                    success=True,
                    content={"type": "text", "content": response.text},
                    status_code=response.status_code,
                    thread_id=response.headers.get('thread_id')
                )
            
        except requests.Timeout:
            error_msg = "Request to webhook timed out"
            self.logger.error(error_msg)
            return MakeResponse(
                success=False,
                content={},
                status_code=504,
                error=error_msg
            )
            
        except requests.RequestException as e:
            error_msg = f"Failed to communicate with webhook: {str(e)}"
            self.logger.error(error_msg)
            return MakeResponse(
                success=False,
                content={},
                status_code=500,
                error=error_msg
            )
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(error_msg)
            return MakeResponse(
                success=False,
                content={},
                status_code=500,
                error=error_msg
            )

# Create singleton instance
make_handler = MakeWebhookHandler()

def send_to_make(message: str) -> str:
    """
    Function to be used by the Make agent to send messages.
    
    Args:
        message (str): Message to send to Make.com
        
    Returns:
        str: Formatted response message
    """
    result = make_handler.send_message(message)
    
    if result.success:
        if isinstance(result.content, dict):
            if result.content.get("type") == "image":
                return f"![Generated Image]({result.content['url']})"
            elif result.content.get("type") == "text":
                return result.content['content']
            else:
                return str(result.content)
        return str(result.content)
    else:
        return f"Error: {result.error}"