from typing import Generator
from openai import OpenAI

BASE_URL = "http://localhost:5555/v1"
MODEL_NAME = "SanctumAI/Meta-Llama-3.1-8B-Instruct-GGUF"


class Model:
    """A class for interacting with the Meta-Llama AI model."""

    def __init__(self, base_url: str = BASE_URL, temperature: float = 0.2):
        """Initialize the Model class.

        Args:
            base_url (str): The base URL for the OpenAI API.
            temperature (float): The temperature for the model's responses.
        """
        self._temperature = temperature
        self._model_name = MODEL_NAME
        self._client = OpenAI(base_url=base_url, api_key="lm-studio")
        self._history = [
            {"role": "system", "content": "You are an intelligent assistant. You always provide well-reasoned answers that are both correct and helpful."},
            {"role": "user", "content": "Hello, introduce yourself to someone opening this program for the first time. Be concise."},
        ]

    def get_response_stream(self, prompt: str, instruction: str = "You are a helpful assistant.") -> Generator[str, None, None]:
        """
        Get a response from the model.

        Args:
            prompt (str): The prompt to give to the model.
            instruction (str): The instruction to give to the model.

        Returns:
            str: The response from the model.
        """
        
        # Append user's prompt to history
        self._history.append({"role": "user", "content": prompt})
        
        
        # Generate the response from the model
        response = self._client.chat.completions.create(
            model=self._model_name,
            messages=self._history,
            temperature=self._temperature,
            stream=True,
        )
    
        # Prepare new assistant message
        new_message = {"role": "assistant", "content": ""}
        
        # Stream the response chunks
        for chunk in response:
            if chunk.choices[0].delta and chunk.choices[0].delta.content:
                chunk_content = chunk.choices[0].delta.content
                new_message["content"] += chunk_content
                yield chunk_content

        # Append the complete assistant response to the history
        self._history.append(new_message)        
        print(self._history)
        
        return new_message["content"]
    
    def add_survey_data(self, data: str):
        '''Add user's registration info to history'''
        self._history.append({ "role": "system", "content": "Here is user's personal information: " + data})