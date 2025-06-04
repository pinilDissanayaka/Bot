from langchain.tools.retriever import create_retriever_tool
from utils import VectorStore


def get_retriever_tool():
    """
        Initializes and returns a retriever tool for answering visitor questions 
        using structured knowledge extracted from the official NoloopTech website.

        This tool enables the AI assistant to search NoloopTech’s services, products, 
        and company information stored in a vector database, and respond accurately 
        to user inquiries during live chat or support sessions.

        Returns:
            A configured retriever tool linked to NoloopTech’s vector store.
    """

    retriever_tool = create_retriever_tool(
        VectorStore().get_vector_store(),
        name="nolooptech_website_knowledge_search",
        description="Search NoloopTech's services, pricing, processes, or product details from structured website data."
    )

    
    return retriever_tool