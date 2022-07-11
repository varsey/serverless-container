import ssl
import smtplib
import datetime
import logging
import platform
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mailer:

    def __init__(self, log: logging, log_filename: str, from_email: str, to_email: str, password: str):
        self.logger = log
        self.log_filename = log_filename
        self.from_email = from_email
        self.to_email = to_email
        self.password = password


    def send_email(self, bodytext: str):
        """отправляем логи на email"""
        subject = "New contractor parsing " + str(datetime.datetime.now())
        body = str(datetime.datetime.now()) + ' ' + str(platform.node()) + ' ' + bodytext

        message = MIMEMultipart()
        message["From"], message["To"], message["Subject"] = self.from_email, self.to_email, subject

        with open(self.log_filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {self.log_filename}")

        message.attach(MIMEText(body, "plain"))
        message.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(self.from_email, self.password)
            server.sendmail(self.from_email, self.to_email, message.as_string())

        return self.logger.info(bodytext)
