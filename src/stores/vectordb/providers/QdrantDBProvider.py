from qdrant_client import models, QdrantClient
import logging
from typing import List

from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
from models.db_schemes import RetrievedDocument

class QdrantDBProvider(VectorDBInterface):
    def __init__(self, db_path: str, distance_method: str):
        
        self.client = None # define inside connect
        self.db_path = db_path
        self.distance_method = None

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.client = QdrantClient(path=self.db_path)
        
    def disconnect(self):
        self.client = None

    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)
    
    def list_all_collection(self) -> List:
        return self.client.get_collections()

    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)

    def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name=collection_name):
            self.logger.info(f"Collection {collection_name} was deleted.")
            return self.client.delete_collection(collection_name=collection_name)
        self.logger.warning(f"Collection {collection_name} was not existed.")
        return None
    
    def create_collection(self, collection_name: str,
                          embedding_size: int,
                          do_reset: bool=False):
        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)
            
        if not self.is_collection_existed(collection_name=collection_name):
            _ = self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )
            self.logger.info(f"Collection '{collection_name}' was created.")
            return True
        
        return False

    def insert_one(self, collection_name: str, text: str, vector: list ,
                          metadata: dict=None,
                          record_id: str=None):
        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Can't insert new record to non-existed collection {collection_name}")
            return False
        
        try:
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id=[record_id],
                        vector=vector,
                        payload={
                            "text": text,
                            "metadata": metadata
                        }
                    )
                ] 
            )
        except Exception as e:
            self.logger.error(f"Error while inserting record: {e}")
            return False
        
        self.logger.info(f"Record was inserted to collection {collection_name}")
        return True
        
    def insert_many(self, collection_name: str, texts: list, vectors: list ,
                          metadata: list=None, record_ids: list=None,
                          batch_size: int=50):
        
        # Beacause I want to Iterate over it
        if metadata is None:
            metadata = [None] * len(texts)
        
        if record_ids is None:
            record_ids = list(range(0,len(texts)))

        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Can't insert new records to non-existed collection {collection_name}")
            return False
        

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size

            batch_record_ids = record_ids[i:batch_end]
            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]

            batch_records = [
                models.Record(
                        id=batch_record_ids[x],
                        vector=batch_vectors[x],
                        payload={
                            "text": batch_texts[x],
                            "metadata": batch_metadata[x]
                        }
                    )
                for x in range(len(batch_texts)) # not batch_size due to last batch may be < 50
            ]

            try:
                _ = self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records
                )
            except Exception as e:
                self.logger.error(f"Error while inserting batch: {e}")
                return False
        
        self.logger.info(f"All records was inserted to collection {collection_name}")
        return True

    def search_by_vector(self, collection_name: str, vector: list ,limit: int=5) -> List[RetrievedDocument]:
        results = self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit 
        )

        if not results or len(results)==0:
            return None
        
        return [
            RetrievedDocument(**{
                "score": result.score,
                "text": result.payload["text"]
            })
            for result in results
        ]
    