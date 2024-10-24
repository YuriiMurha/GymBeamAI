from openai import OpenAI

BASE_URL = "http://localhost:5555/v1"
MODEL_NAME = "SanctumAI/Meta-Llama-3.1-8B-Instruct-GGUF"


class Model:
    """A class for interacting with the Meta-Llama AI model."""

    def __init__(self, base_url: str = BASE_URL, temperature: float = 0.7):
        """Initialize the Model class.

        Args:
            base_url (str): The base URL for the OpenAI API.
            temperature (float): The temperature for the model's responses.
        """
        self._temperature = temperature
        self._model_name = MODEL_NAME
        self._client = OpenAI(base_url=base_url, api_key="lm-studio")

    def get_response(self, prompt: str, instruction: str = "You are a helpful assistant.") -> str:
        """
        Get a response from the model.

        Args:
            prompt (str): The prompt to give to the model.
            instruction (str): The instruction to give to the model.

        Returns:
            str: The response from the model.
        """
        response = self._client.chat.completions.create(
            model=self._model_name,
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": prompt},
            ],
            temperature=self._temperature,
        )
        
        return response.choices[0].message.content


if __name__ == "__main__":
    model = Model()
    response = model.get_response("Hello, World!")
    print(response)

