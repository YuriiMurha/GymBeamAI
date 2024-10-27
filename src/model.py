import csv
import json
import os
from typing import Generator
import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse

BASE_URL = "http://localhost:5555/v1"
MODEL_NAME = "gemini-pro"  # Gemini's model name
API_KEY = 'AIzaSyCqFJJD0F1U-4g4YD1Eec7ycE-t25t52xo' # Your Gemini API key

SYSTEM_RECOMMENDATION = '''system: You MUST respond with a brief intro and a recomendation of a ONE or TWO particular GymBeam products from the LIST of products you were provided.You WILL STRICTLY recommend it by answering with an HTML code of title as a heading text with link property as href, then you MUST ALWAYS add an \"img\" tag STRICTLY with this style <width=\"200\" height=\"200\" style=\"border-radius: 10%; overflow: hidden;\" and then provide a price, description and dosage in bold. After that, provide reasons why this user should buy this product based on his personal health information. Here is the user's personal information about health in format \"age,gender,weight,height,activityLevel,healthCondition,goal,drugUsage,allergies,diet\":'''
SYSTEM_NOTE = "Please keep your answers short and concise. For plain text you can use both Markdown or HTML notation, but for HTML you MUST use HTML tags, not Markdown monospacecode blocks."
DEFAULT_USER_INFO = "General health,40,Muž,80,180,\"3x týdně kolektivní sport, 2x týdně posilovna\",\"Zvýšený cholesterol, Zvýšený krevní tlak, Snížené hladiny omega-3 v krvi, Inzulinová rezistence ve stádiu prediabetu\",\"Zlepšit krevní hodnoty (cholesterol, omega-3, glykemie) + snížit krevní tlak\",\"Hypolipidemika (Léky na cholesterol), Antihypertenziva (Léky na tlak)\",Alergie na sóju,\"Přerušovaný půst 16:8, má nízký příjem ovoce a zeleniny a má málo vlákniny ve stravě\""
OUTPUT_FORMAT= 'recommended_product;recommended_dosage;text_of_recommendation'

class Model:
    """A class for interacting with the Gemini AI model."""

    def __init__(self, products: str, api_key: str = API_KEY, temperature: float = 0.01):
        """Initialize the Model class.

        Args:
            api_key (str): The API key for Gemini.
            temperature (float): The temperature for the model's responses.
            products (str): The list of products to recommend.
        """
        self._model_name = MODEL_NAME
        self._user_info = ""
        self._config = genai.types.GenerationConfig(
            temperature=temperature,
            candidate_count=1,
            max_output_tokens=2048,
        )
        
        # Configure safety settings to minimum
        safety_settings = {
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
            "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE"
        }
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        # Initialize model with disabled safety settings
        self._model = genai.GenerativeModel(
            MODEL_NAME,
            safety_settings=safety_settings,
            generation_config=self._config
        )
        
        # Initialize chat
        self._history = self._model.start_chat(history=[])
        
        # Add initial context
        self._add_context_messages([
            "System: You are an intelligent health assistant for purchasing products. PLEASE, keep your answers consise and follow ALL system instructions.",
            "System: Here is the LIST of GymBeam products that you MUST recommend in EVERY response (Please choose only ONE product to represent as HTML): " + products,
        ])

    def _add_context_messages(self, messages: list[str]):
        """Add context messages to the chat history."""
        for msg in messages:
            response = self._history.send_message(msg)
            response.resolve()  # Wait for the response to complete

    def get_response_stream(self, prompt: str) -> Generator[str, None, None]:
        """
        Get a streaming response from the model.

        Args:
            prompt (str): The prompt to give to the model.

        Returns:
            Generator[str, None, None]: A generator yielding response chunks.
        """
        # Generate the response from the model
        response = self._history.send_message(
            "user's prompt: " + prompt + SYSTEM_RECOMMENDATION + self._user_info + SYSTEM_NOTE,
            generation_config=self._config,
            stream=True
        )

        # Stream the response chunks
        for chunk in response:
            if chunk.text:
                yield chunk.text
        
        summary = self.summarize_response(response.text)
        for row in summary:
            product, dosage, recommendation = row.split(';') if ';' in row else row.split(',')
            
            self.save_output_to_csv({
                'persona_id': '0',
                'persona_name': '',
                'recommended_product': product,
                'recommended_dosage': dosage,
                'text_of_recommendation': recommendation,
                'source_of_recommendation': self.find_source(product),
            })
    
    def find_source(self, product : str):
        # Delete the history
        self._history = self._model.start_chat(history=[])  
        keyword = self._create_keyword(self._get_keywords(), product)
        return self._get_research(keyword)
    
    def _create_keyword(self, keywords : list[str], product : str):
        return self._history.send_message(
            "SYSTEM: RESPOND ONLY STRICTLY ONE WORD AND DO NOT WRITE ANY OTHER TEXT. DETERMINE THE KEYWORD THAT CORRESPONDS TO THIS PRODUCT: \"" + product + "\". RESPOND WITH ONE OF THESE KEYWORDS: " + ', '.join(keywords),
            generation_config=self._config
        ).text

    def _get_keywords(self) -> list[str]:
        """Get a list of JSON disctionary's keys"""
        with open(r'./src/data/researches/keywords_count.json', encoding='utf-8') as f:
            return [str(key) for key in json.load(f).keys()]

    def _get_research(self, key : str) -> str:
        """Get a JSON disctionary's value"""
        with open(r'./src/data/researches/keywords_pdf.json', encoding='utf-8') as f:
            return json.load(f)[key.lower()][0]

    def add_survey_data(self, user_info : str = DEFAULT_USER_INFO):
        '''Add user's registration info to model'''
        self._user_info = user_info
        
    def save_to_csv(self, data):
        '''
        Save survey data to a CSV file.
        '''
        with open(r'./src/data/users/user_data.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(data)
            
    def save_output_to_csv(self, data):
        '''
        Save output data to a CSV file.
        '''
        with open(r'./src/data/users/output_data.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(data)

    def summarize_response(self, response : str):
        '''Summarize response by sending it to the model'''
        
        return self._history.send_message(
            "SYSTEM: RESPOND ONLY STRICTLY IN THIS FORMAT AND DO NOT WRITE ANY OTHER TEXT: \"" + OUTPUT_FORMAT + "\". FOR EACH PRODUCT GIVE ME EXACTLY THREE SEMICOLON SEPARATED VALUES THAT CORRESPOND TO YOUR RESPONSE, EACH PRODUCT SHOULD BE IN DIFFERENT LINE, use '\n' for separating them: " + response,
            generation_config=self._config,
            stream=False
        ).text.split('\n')
        