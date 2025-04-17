from langchain.tools.retriever import create_retriever_tool
from utils import VectorStore


def get_retriever_tool(web_name):
    """
    Return a retriever tool that is able to search and retrieve information from a given web_name's vector store.

    Args:
        web_name (str): The name of the website to get a retriever tool for.

    Returns:
        retriever_tool (RetrieverTool): A retriever tool that is able to search and retrieve information from the given web_name's vector store.
    """
    retriever_tool = create_retriever_tool(
        VectorStore().get_vector_store(web_name=web_name),
        name=f"retrieve_{web_name}_info",
        description=f"Use this tool to search and answer questions using knowledge extracted from the website '{web_name}'."
    )

    
    return retriever_tool