"""
AI Service Module for LLM interactions using LangChain and OpenAI.

This module provides a modular and reusable service for sending text and optional images
to an LLM and receiving responses.
"""

import os
import base64
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_core.prompts import ChatPromptTemplate
except ImportError as e:
    raise ImportError(
        "Required dependencies not installed. Please install: pip install langchain-openai langchain-core"
    ) from e


class AIService:
    """
    A modular AI service for interacting with LLMs using LangChain and OpenAI.
    
    This service can handle text prompts and optional images, providing a clean
    interface for LLM interactions.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_message: Optional[str] = None
    ):
        """
        Initialize the AI service.
        
        Args:
            api_key: OpenAI API key. If None, will use OPENAI_API_KEY environment variable
            model: The model to use (default: gpt-4o for vision support)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response
            system_message: Optional system message to set context
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_message = system_message
        
        # Initialize the LangChain ChatOpenAI instance
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
    
    def _encode_image(self, image_path: Union[str, Path]) -> str:
        """
        Encode an image file to base64 string.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image string
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            Exception: If image encoding fails
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to encode image: {e}") from e
    
    def _create_image_content(self, image_data: Union[str, Path], image_type: str = "auto") -> Dict[str, Any]:
        """
        Create image content for the message.
        
        Args:
            image_data: Either a file path or base64 encoded string
            image_type: Image type (auto-detect if "auto")
            
        Returns:
            Dictionary containing image content for the message
        """
        # If it's a file path, encode it
        if isinstance(image_data, (str, Path)) and Path(image_data).exists():
            base64_image = self._encode_image(image_data)
            if image_type == "auto":
                image_type = Path(image_data).suffix.lower().replace('.', '')
        else:
            # Assume it's already base64 encoded
            base64_image = str(image_data)
            if image_type == "auto":
                image_type = "png"  # Default fallback
        
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/{image_type};base64,{base64_image}"
            }
        }
    
    def query(
        self,
        prompt: str,
        image: Optional[Union[str, Path, List[Union[str, Path]]]] = None,
        system_message: Optional[str] = None
    ) -> str:
        """
        Send a query to the LLM with optional image(s).
        
        Args:
            prompt: The text prompt to send
            image: Optional image(s) - can be file path(s) or base64 string(s)
            system_message: Optional system message to override default
            
        Returns:
            The LLM's response text
            
        Raises:
            Exception: If the LLM request fails
        """
        try:
            messages = []
            
            # Add system message if provided
            current_system_message = system_message or self.system_message
            if current_system_message:
                messages.append(SystemMessage(content=current_system_message))
            
            # Prepare the human message content
            content = []
            
            # Add text content
            content.append({
                "type": "text",
                "text": prompt
            })
            
            # Add image(s) if provided
            if image:
                images = image if isinstance(image, list) else [image]
                for img in images:
                    if img:  # Skip None/empty images
                        content.append(self._create_image_content(img))
            
            # Create human message
            messages.append(HumanMessage(content=content))
            
            # Get response from LLM
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            raise Exception(f"Failed to get LLM response: {e}") from e
    
    def simple_query(self, prompt: str) -> str:
        """
        Simple text-only query method for convenience.
        
        Args:
            prompt: The text prompt to send
            
        Returns:
            The LLM's response text
        """
        return self.query(prompt)
    
    def update_config(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_message: Optional[str] = None
    ):
        """
        Update the service configuration.
        
        Args:
            model: New model to use
            temperature: New temperature setting
            max_tokens: New max tokens setting
            system_message: New system message
        """
        if model:
            self.model = model
        if temperature is not None:
            self.temperature = temperature
        if max_tokens is not None:
            self.max_tokens = max_tokens
        if system_message is not None:
            self.system_message = system_message
        
        # Recreate the LLM instance with new settings
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )


# Convenience function for quick usage
def quick_query(prompt: str, image: Optional[Union[str, Path]] = None, **kwargs) -> str:
    """
    Quick convenience function for one-off queries.
    
    Args:
        prompt: The text prompt to send
        image: Optional image file path or base64 string
        **kwargs: Additional arguments for AIService initialization
        
    Returns:
        The LLM's response text
    """
    service = AIService(**kwargs)
    return service.query(prompt, image)


# Example usage
if __name__ == "__main__":
    # Example 1: Simple text query
    service = AIService()
    response = service.simple_query("What is the capital of France?")
    print(f"Response: {response}")
    
    # Example 2: Query with image
    # response = service.query("Describe this image", image="path/to/image.jpg")
    # print(f"Image analysis: {response}")
    
    # Example 3: Quick query function
    # response = quick_query("Explain quantum computing in simple terms")
    # print(f"Quick response: {response}")
