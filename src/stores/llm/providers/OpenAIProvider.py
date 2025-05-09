from openai import OpenAI
import logging

from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnums

class OpenAIProvider(LLMInterface):

    def __init__(self, api_key: str, api_url: str=None,
                 default_input_max_characters: int=1000,
                 default_generation_max_output_tokens: int=1000,
                 default_generation_temperature: float=0.1):
        
        self.api_key = api_key
        self.api_url = api_url
        
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        # Need in the future
        self.generate_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(
            api_key = self.api_key,
            base_url= self.api_url if self.api_key and len(self.api_key) else None
        )

        self.enums = OpenAIEnums
        # __name__ this mean take name of the file name
        self.logger = logging.getLogger(__name__)

    # self.generate_model_id = model_id beacuse I can change it will app is running
    #  if it in init I need to config it on first and can't change
    def set_generation_model(self, model_id: str):
        self.generate_model_id = model_id


    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
    

    def generate_text(self, prompt: str, chat_history: list=[],
                      max_output_tokens: int=None, temperature: float=None):
        if not self.client:
            self.logger.error("OpenAI client was not set.")
            return None
        
        if not self.generate_model_id:
            self.logger.error("Generation model for OpenAI was not set.")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        chat_history.append(
            self.construct_prompt(
                prompt=prompt,
                role=OpenAIEnums.USER.value
            )
        )
    
        response = self.client.chat.completions.create(
            model= self.generate_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature
        )

        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("Error while generation text with OpenAI")
            return None
        
        return response.choices[0].message.content
 

    def embed_text(self, text: str, document_type: str=None):
        if not self.client:
            self.logger.error("OpenAI client was not set.")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for OpenAI was not set.")
            return None
        
        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model_id,
        )

        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Error while embedding text with OpenAI")
            return None

        return response.data[0].embedding

    def construct_prompt(self, prompt: str, role: str):

        return {
            "role": role,
            "content": self.process_text(prompt)
        }
    
    def process_text(self, text: str):
        # Cut if to large and remove start and end /n and space
        return text[:self.default_input_max_characters].strip()