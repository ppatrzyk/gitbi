"""
Format and send email
"""
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import repo
import smtplib

def send(report, to):
    """
    Main function for sending alerts/reports
    """
    assert to is not None, "no email provided"
    smtp_user, smtp_pass, smtp_url, smtp_email = repo.get_email_params()
    url, port = smtp_url.split(":")
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Gitbi report"
    msg['From'] = smtp_email
    msg['To'] = to
    msg.attach(MIMEText("Requires html", 'plain'))
    msg.attach(MIMEText(report.body.decode(), "html"))
    with smtplib.SMTP(url, port) as server:
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_email, to, msg.as_string())
    return True
