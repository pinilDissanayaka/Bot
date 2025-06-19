from langchain.tools.retriever import create_retriever_tool
from utils import VectorStore


def get_retriever_tool(web_name:str):
    f"""
        Initializes and returns a retriever tool for answering visitor questions 
        using structured knowledge extracted from the official {web_name} website.

        This tool enables the AI assistant to search NoloopTech’s services, products, 
        and company information stored in a vector database, and respond accurately 
        to user inquiries during live chat or support sessions.

        Returns:
            A configured retriever tool linked to {web_name}'s vector store.
    """

    retriever_tool = create_retriever_tool(
        VectorStore(web_name=web_name).get_vector_store(),
        name=f"{web_name}_website_knowledge_search",
        description=f"Search {web_name} services, pricing, processes, or product details from structured website data."
    )

    
    return retriever_tool