"""
Format and send email
"""
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import repo
import smtplib

def send(report, format, to, file_name):
    """
    Main function for sending alerts/reports
    """
    assert to is not None, "no email provided"
    smtp_user, smtp_pass, smtp_url, smtp_email = repo.get_email_params()
    url, port = smtp_url.split(":")
    content = report.body.decode()
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Gitbi report: {file_name}"
    msg['From'] = smtp_email
    msg['To'] = to
    match format:
        case "html":
            msg.attach(MIMEText("Requires html", 'plain'))
            msg.attach(MIMEText(content, "html"))
        case "text":
            msg.attach(MIMEText(content, 'plain'))
        case "csv" | "json":
            msg.attach(MIMEText(file_name, 'plain'))
            result = MIMEBase('application', "octet-stream")
            result.set_payload(content)
            encoders.encode_base64(result)
            result.add_header("Content-Disposition", f"attachment; filename={file_name}.{format}")
            msg.attach(result)
    with smtplib.SMTP(url, port) as server:
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_email, to, msg.as_string())
    return True
