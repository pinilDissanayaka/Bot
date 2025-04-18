from langchain.tools.retriever import create_retriever_tool
from utils import VectorStore


def get_retriever_tool():
    """
        Creates and returns a retriever tool for searching and answering questions
        using information extracted from the NoloopTech website.

        This function initializes a retriever tool using the vector store associated
        with the NoloopTech website. The retriever tool can be utilized to search
        and extract knowledge from the stored data to answer relevant questions.

        Returns:
            A retriever tool configured with the NoloopTech website vector store.
    """

    retriever_tool = create_retriever_tool(
        VectorStore().get_vector_store(),
        name="retrieve_nolooptech_info",
        description="Use this tool to search and answer questions using knowledge extracted from the website NoloopTech."
    )

    
    return retriever_tool