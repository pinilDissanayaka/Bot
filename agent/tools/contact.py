import os
import psycopg2
import smtplib
from email.utils import formataddr
from email.mime.text import MIMEText
from langchain_core.tools import tool
from dotenv import load_dotenv, find_dotenv
from database import get_db
from database.models import Lead
from langchain_core.runnables import RunnableConfig


load_dotenv(find_dotenv())


@tool
def contact(name: str, senders_email: str, phone_number: str, message_body: str, config:RunnableConfig) -> str:
    """
    A tool that saves the contact details to the database.

    This tool takes four parameters: name, senders_email, phone_number, and message_body.
    It uses the environment variables HOST, EMAIL_API_KEY, SENDER, and RECEIVER to send an email.
    It also uses the DATABASE_URL environment variable to connect to the database and insert the contact details.

    Returns a string with a success message or an error message if there was an exception.
    """
    try:
        
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        
        configuration = config.get("configurable", {})
        
        thread_id = configuration.get("thread_id", "12423534")
        
        
        cur= conn.cursor()
        
        query = "INSERT INTO lead (thread_id, name, email, phone, message) VALUES (%s, %s, %s, %s, %s)"
        
        cur.execute(query, (thread_id, name, senders_email, phone_number, message_body))
        
        conn.commit()
        
        cur.close()
        conn.close()        

        return "Thank you, our team will get back to you soon."

    except Exception as e:
        return "An error occurred while processing your request. Please try again later."