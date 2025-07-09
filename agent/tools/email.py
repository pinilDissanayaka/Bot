import os
import psycopg2
import smtplib
from email.utils import formataddr
from email.mime.text import MIMEText
from langchain_core.tools import tool
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


@tool
def contact(name: str, senders_email: str, phone_number: str, message_body: str) -> str:
    """
    A tool that sends an email and saves the contact details to the database.

    This tool takes four parameters: name, senders_email, phone_number, and message_body.
    It uses the environment variables HOST, EMAIL_API_KEY, SENDER, and RECEIVER to send an email.
    It also uses the DATABASE_URL environment variable to connect to the database and insert the contact details.

    Returns a string with a success message or an error message if there was an exception.
    """
    try:
        conn= psycopg2.connect(os.getenv("DATABASE_URL"))
        cursor = conn.cursor()
        # Insert contact details into the database
        cursor.execute(
            "INSERT INTO lead (name, email, phone, message) VALUES (%s, %s, %s, %s)",
            (name, senders_email, phone_number, message_body)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return "Email sent successfully!, our team will get back to you soon."

    except Exception as e:
        return str(e)