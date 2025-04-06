from typing import List
import json

from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum

class NLPController(BaseController):
    
    def __init__(self, vectordb_client, generation_client,
                embedding_client, template_parser):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)

    def get_vector_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)
        
        # Convert collection_info into a json string "default=lambda x: x.__dict__" this means
        #  if you can't handle it convert object of class to dictionary
        #  then we convert it to dict again using json.loads
        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )
    
    def index_info_vector_db(self, project: Project, chunks: List[DataChunk],
                              chunks_ids: List[int],
                              do_reset: bool=False):
        # step1: get collection_name
        collection_name = self.create_collection_name(project_id=project.project_id)
        
        # step2: manage chunk items
        texts = [ chunk.chunk_text for chunk in chunks ]
        metadata = [ chunk.chunk_metadata for chunk in chunks ]
        vectors=[
            self.embedding_client.embed_text(
                text = text,
                document_type = DocumentTypeEnum.DOCUMENT.value
            )
            for text in texts
        ]
    
        # step3: create collection is not exist
        _ = self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset
        )

        # step4: insert into vector db 
        _ = self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts, 
            vectors=vectors,
            metadata=metadata,
            record_ids=chunks_ids
        )

        return True
    
    def search_vector_db_collection(self, project: Project, text: str, limit: int=10):
        # step1: Get collection name 
        collection_name = self.create_collection_name(project_id=project.project_id)

        # step2: Get text embedding Vector
        vector = self.embedding_client.embed_text(
                text = text,
                document_type = DocumentTypeEnum.QUERY.value
        )
        
        if not vector or len(vector)==0:
            return False
        
        # step3: do semantic search
        results = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )

        if not results:
            return False
        
        return results
    
    def answer_rag_question(self, project: Project, query: str, limit: int=10):
        
        answer, full_prompt, chat_history = None, None, None

        # step1: Retrieve related documents 
        retrieved_documents = self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit,
        )

        if not retrieved_documents or len(retrieved_documents)==0:
            return answer, full_prompt, chat_history
    
        # Step2: Construct LLM Prompt
        system_prompt = self.template_parser.get(
            group="rag",
            key="system_prompt",
        )

        document_prompts = "\n".join([
            self.template_parser.get(
                group="rag",
                key="document_prompt",
                vars={
                    "doc_num": idx + 1,
                    "chunk_text": doc.text
                }
            )
            for idx, doc in enumerate(retrieved_documents)
        ])

        footer_prompt = self.template_parser.get(
            group="rag",
            key="footer_prompt",
            vars={
                "query" : query
            }
        )

        # Create Prompts
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value)
        ]

        full_prompt = "\n\n".join([document_prompts, footer_prompt])

        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history,
        )

        return answer, full_prompt, chat_history
