from openai import OpenAI
from typing import List, Dict, Generator

client = OpenAI()

def reason_with_o1(
    messages: List[Dict[str, str]], 
) -> Generator[str, None, None]:
    """
    Stream chat completions from OpenAI API.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
    
    Yields:
        Content chunks from the streaming response
        
    Example:
        messages = [
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
        model="o1-preview",
        messages=messages,
        stream=True,
    )
    
    # Yield content from chunks
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content