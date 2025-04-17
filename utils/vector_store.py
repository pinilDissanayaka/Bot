import os
import shutil
from .config import embeddings, llm
from langchain_experimental.text_splitter import SemanticChunker
from langchain_chroma import Chroma


class VectorStore:
    def __init__(self) -> None:
        """
        Initialize a VectorStore object.

        This creates a base directory for storing the vector stores at ./vector.
        The directory is created if it does not exist.

        """
        self.BASE_VECTOR_STORE_DIR = os.path.join(os.getcwd(), "vector")
        os.makedirs(self.BASE_VECTOR_STORE_DIR, exist_ok=True)
        
    def _get_store_path(self, web_name: str) -> str:
        """
        Generate the file path for a given web_name's vector store.

        Args:
            web_name (str): The name of the website for which to generate the vector store path.

        Returns:
            str: The full path where the vector store for the given web_name is stored.
        """
        return os.path.join(self.BASE_VECTOR_STORE_DIR, web_name)

    def create_vector_store(self, web_name: str, content: list|str):
        """
        Creates a vector store for a given website name with the provided content.

        This method generates a vector store using the provided content, which can be a string or a list of strings. 
        The content is first chunked into documents using a semantic chunker, and these documents are then stored 
        as embeddings in a Chroma vector store.

        Args:
            web_name (str): The name of the website for which to create the vector store.
            content (list|str): The content to be processed and stored. Can be a single string or a list of strings.

        Returns:
            str: The name of the website, confirming the creation of the vector store.

        Raises:
            ValueError: If no documents are created from the provided content.
        """
        store_path=self._get_store_path(web_name=web_name)
        
        if isinstance(content, str):
            content = [content]
        
        
        chunker=SemanticChunker(embeddings=embeddings)
        
        docs=chunker.create_documents(content)
        
        if not docs:
            raise ValueError(f"No documents found for: {web_name}")
        
        vector_store = Chroma(
            collection_name=f"{web_name}",
            embedding_function=embeddings,
            persist_directory=store_path, 
        )
        
        vector_store.add_documents(docs)
        
        return web_name
            
    def get_vector_store(self, web_name: str):
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
        store_path=self._get_store_path(web_name=web_name)

        if not os.path.exists(store_path):
            raise ValueError(f"No vector store found for: {web_name}")
        
        
        vector_store = Chroma(
            collection_name=f"{web_name}",
            embedding_function=embeddings,
            persist_directory=store_path,  
        )
        
        return vector_store.as_retriever(search_kwargs={"k": 3})
    
    def delete_vector_store(self, web_name: str):
        """
        Deletes a vector store for a given website name.

        This method deletes the vector store directory for the given website name. If the directory does not exist, no action is taken.

        Args:
            web_name (str): The name of the website for which to delete the vector store.
        """
        store_path=self._get_store_path(web_name=web_name)
        
        if os.path.exists(store_path):
            shutil.rmtree(store_path)
    
    

        


