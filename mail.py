import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from email.mime.base import MIMEBase
from email import encoders

def send_html_gmail(mail_address : str, app_pass : str, to : list, title : str, html : str, cc = [], bcc = []):
    message = MIMEMultipart()
    message['Subject'] = title
    message['From'] = mail_address
    message['To'] = ",".join(to)
    message['Cc'] = ",".join(cc)
    message['Bcc'] = ",".join(bcc)
    message['Date'] = formatdate()
    message.attach(MIMEText(html, 'html'))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as server:
        server.login(mail_address, app_pass)
        server.send_message(message)
        server.close()

def send_file_gmail(mail_address : str, app_pass : str, to : list, title : str, text : str, file : list, cc = [], bcc = []):
    message = MIMEMultipart()
    message['Subject'] = title
    message['From'] = mail_address
    message['To'] = ",".join(to)
    message['Cc'] = ",".join(cc)
    message['Bcc'] = ",".join(bcc)
    message['Date'] = formatdate()
    message.attach(MIMEText(text, "plain"))
    for filename in file:
        with open(filename, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
        message.attach(part)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as server:
        server.login(mail_address, app_pass)
        server.send_message(message)
        server.close()