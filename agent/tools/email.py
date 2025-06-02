import smtplib
from langchain_core.tools import tool

@tool
def contact(senders_email:str, message:str):
    """
    Send an email from a given sender with a given message.
    If the Agent dont know the specific answer, it will use this tool.
    
    Parameters:
    senders_email (str): The email address of the sender.
    message (str): The message to be sent.
    
    Returns:
    str: A success message if the email is sent, otherwise the exception message.
    """
    
    try:
        """# creates SMTP session
        s = smtplib.SMTP('smtp.gmail.com', 587)
        # start TLS for security
        s.starttls()
        # Authentication
        s.login("pinildissanayka@gmail.com", "")
        # sending the mail
        s.sendmail(senders_email, "pinildissanayka@gmail.com" , message)
        # terminating the session
        s.quit()"""
        
        print(f"Sending email from {senders_email} with message: {message}")
        # Simulate sending an email
        return "Email sent successfully!" 
    except Exception as e:
        return e