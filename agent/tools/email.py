import os
import smtplib
from email.utils import formataddr
from email.mime.text import MIMEText
from langchain_core.tools import tool
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


@tool
def contact(senders_email: str, message_body: str):
    """
        Sends a contact email using SMTP with credentials and email addresses from environment variables.

        This function sends an email containing the given message from the specified sender's email
        to a predefined recipient. 

        Args:
            senders_email (str): The email address of the user initiating the contact.
            message_body (str): The body of the message to be sent.

        Returns:
            str: A success message if the email was sent successfully, or an error message if an exception occurred.

        Raises:
            ValueError: If required environment variables (SENDER or RECEIVER) are missing.
    """
    try:
        smtp_host = os.getenv("HOST")
        smtp_port = 587
        smtp_user = "api"
        smtp_pass = os.getenv("EMAIL_API_KEY")
        sender_email = os.getenv("SENDER")
        receiver_email = os.getenv("RECEIVER")

        if not sender_email or not receiver_email:
            raise ValueError("Missing SENDER or RECEIVER in environment variables")

        msg = MIMEText(f"Message from: {senders_email}\n\n{message_body}")
        msg["Subject"] = f"Contact from {senders_email}"
        msg["From"] = formataddr(("Private Person", sender_email))
        msg["To"] = formataddr(("A Test User", receiver_email))

        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        return "Email sent successfully!, our team will get back to you soon."

    except Exception as e:
        return str(e)
    
    
