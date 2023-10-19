from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from email.mime.base import MIMEBase
from email import encoders
import smtplib, ssl

def send_html_gmail(mail_address : str, app_pass : str, to : list, title : str, html : str):
    for i in to:
        smtpobj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpobj.ehlo()
        smtpobj.starttls()
        smtpobj.ehlo()
        smtpobj.login(mail_address, app_pass)
        msg = MIMEText(html, "html")
        msg['Subject'] = title
        msg['From'] = mail_address
        msg['To'] = i
        msg['Date'] = formatdate()

        smtpobj.sendmail(mail_address, i, msg.as_string())
        smtpobj.close()

def send_file_gmail(mail_address : str, app_pass : str, to : list, title : str, text : str, file : list):
    for i in to:
        _msg = MIMEMultipart()
        _msg['From'] = mail_address
        _msg['To'] = i
        _msg['Subject'] = title
        _msg['Date'] = formatdate(timeval=None, localtime=True)
        _msg.attach(MIMEText(text, "plain"))
        for filename in file:
            with open(filename, 'rb') as _f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(_f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename= {}'.format(filename))
            _msg.attach(part)
        context = ssl.create_default_context()
        _smtp = smtplib.SMTP_SSL(host='smtp.gmail.com', port=465, timeout=10, context=context)
        _smtp.login(user=mail_address, password=app_pass)
        _smtp.sendmail(mail_address, i, _msg.as_string())
        _smtp.close()