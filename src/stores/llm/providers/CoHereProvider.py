import cohere
import logging

from ..LLMInterface import LLMInterface
from ..LLMEnums import CoHereEnums, DocumentTypeEnum

class CoHereProvider(LLMInterface):

    def __init__(self, api_key: str, default_input_max_characters: int=1000,
                 default_generation_max_output_tokens: int=1000,
                 default_generation_temperature: float=0.1):
        
        self.api_key = api_key
        
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        # Need in the future
        self.generate_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.Client(
            api_key = self.api_key,
        )

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
            self.logger.error("CoHere client was not set.")
            return None
        
        if not self.generate_model_id:
            self.logger.error("Generation model for CoHere was not set.")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        chat_history.append(
            self.construct_prompt(
                prompt=prompt,
                role=CoHereEnums.USER.value
            )
        )
    
        response = self.client.chat(
            model= self.generate_model_id,
            chat_history=chat_history,
            messages=self.process_text(prompt),
            max_tokens=max_output_tokens,
            temperature=temperature
        )

        if not response or not response.text:
            self.logger.error("Error while generation text with CoHere")
            return None
        
        return response.text
 

    def embed_text(self, text: str, document_type: str=None):
        if not self.client:
            self.logger.error("CoHere client was not set.")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere was not set.")
            return None
        
        input_type = CoHereEnums.DOCUMENT.value
        if document_type == DocumentTypeEnum.QUERY.value:
            input_type = CoHereEnums.QUERY.value

        response = self.client.embed(
            texts=[self.process_text(text)],
            model=self.embedding_model_id,
            input_type=input_type,
            embedding_types=['float']
        )

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while embedding text with CoHere")
            return None

        return response.embeddings.float[0] # one text

    def construct_prompt(self, prompt: str, role: str):

        return {
            "role": role,
            "text": self.process_text(prompt)
        }
    
    def process_text(self, text: str):
        # Cut if to large and remove start and end /n and space
        return text[:self.default_input_max_characters].strip()