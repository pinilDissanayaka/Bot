import os
import shutil
from .config import embeddings
from langchain_chroma import Chroma


class VectorStore:
    def __init__(self, web_name:str="nolooptech") -> None:
        """
        Initialize a VectorStore object.

        This creates a base directory for storing the vector stores at ./vector.
        The directory is created if it does not exist.

        """
        self.BASE_VECTOR_STORE_DIR = os.path.join(os.getcwd(), "vector")
        self.web_name = web_name
    
        os.makedirs(self.BASE_VECTOR_STORE_DIR, exist_ok=True)
        
    def _get_store_path(self) -> str:
        """
            Constructs the full path to the vector store directory for the current website.

            This method combines the base vector store directory with the website name
            to generate the full path where the vector store is stored.

            Returns:
                str: The full path to the vector store directory for the current website.
        """
        return os.path.join(self.BASE_VECTOR_STORE_DIR, self.web_name)
    
    def create_vector_store(self, text: list):
        """
        Creates a vector store for a given website name.

        This method generates a Chroma vector store using the provided documents and the embeddings stored in the vector store
        for the given website name. If no vector store is found, a ValueError is raised.

        Args:
            documents (list): A list of documents to be added to the vector store.

        Returns:
            langchain.tools.retriever.RekeeperRetriever: A retriever which can be used to search the vector store.
        """
        store_path=self._get_store_path()

        
        vector_store = Chroma(
            collection_name=f"{self.web_name}",
            embedding_function=embeddings,
            persist_directory=store_path,  
        )
        
        vector_store.add_texts(texts=text)
        
                    
    def get_vector_store(self):
        """
        Gets a vector store for a given website name.

        This method generates a Chroma vector store using the embeddings stored in the vector store
        for the given website name. If no vector store is found, a ValueError is raised.

        Args:
            web_name (str): The name of the website for which to get the vector store.

        Returns:
            langchain.tools.retriever.RekeeperRetriever: A retriever which can be used to search the vector store.

        Raises:
            ValueError: If no vector store found for the given website name.
        """
        store_path=self._get_store_path()

        if not os.path.exists(store_path):
            raise ValueError(f"No vector store found for: {self.web_name}")
        
        
        vector_store = Chroma(
            collection_name=f"{self.web_name}",
            embedding_function=embeddings,
            persist_directory=store_path,  
        )
        
        return vector_store.as_retriever(search_kwargs={"k": 3})
    
    def delete_vector_store(self):
        """
        Deletes a vector store for a given website name.

        This method deletes the vector store directory for the given website name. If the directory does not exist, no action is taken.

        Args:
            web_name (str): The name of the website for which to delete the vector store.
        """
        store_path=self._get_store_path(web_name=self.web_name)
        
        if os.path.exists(store_path):
            shutil.rmtree(store_path)
    
    

        


