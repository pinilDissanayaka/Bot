import os
import smtplib
from langchain_core.tools import tool
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


@tool
def contact(senders_email:str, message:str):
    """
    Send an email from a given sender with a given message.
    
    Parameters:
    senders_email (str): The email address of the sender.
    message (str): The message to be sent.
    
    Returns:
    str: A success message if the email is sent, otherwise the exception message.
    """
    
    try:
        message = f"""\
            Subject: Contact from {senders_email}
            From: {senders_email}
            {message}
        """
            

        with smtplib.SMTP(os.getenv("SENDERS_EMAIL"), 587) as server:
            server.starttls()
            server.login("api", os.getenv("EMAIL_API_KEY"))
            server.sendmail(senders_email, os.getenv("RECEIVERS_EMAIL"), message)

        return "Email sent successfully!"
    
    except Exception as e:
        return e
    
    
