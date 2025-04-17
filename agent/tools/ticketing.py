from langchain_core.tools import tool

@tool
def issue_ticket(question:str):
    """
    
    Creates a ticket based on the provided question this tool used when agent dont know the answer.

    Args:
        question (str): The question or issue to be addressed in the ticket.

    Returns:
        str: A confirmation message indicating that the ticket has been issued or not.
    """

    return "Ticket issued"