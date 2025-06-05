import smtplib

sender = "hello@demomailtrap.co"
receiver = "pinildissanayaka@gmail.com"

message = f"""\
Subject: Hi Mailtrap
To: {receiver}
From: {sender}

This is a test e-mail message."""

with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
    server.starttls()
    server.login("api", "b842505a32acf6d591ad88168a32acc1")
    server.sendmail(sender, receiver, message)