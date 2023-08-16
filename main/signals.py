import os
import smtplib
import ssl
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.conf import settings
from django.db.models.signals import pre_delete, post_save
from django.dispatch.dispatcher import receiver

from .models import Document, ApprovalRequest


@receiver(pre_delete, sender=Document)
def delete_document_file(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(post_save, sender=ApprovalRequest)
def send_approval_request_email(sender, instance, **kwargs):
    receivers = instance.receivers.all()
    document = instance.document
    sender_name = instance.sender.get_full_name()  # Get the email of the user who created the request

    subject = f'Запрос на подтверждение документа: {document.description}'

    port = settings.EMAIL_PORT
    smtp_server = settings.EMAIL_HOST
    sender_email = settings.EMAIL_HOST_USER
    password = settings.EMAIL_HOST_PASSWORD
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    for r in receivers:
        message = f': Дорогой/ая {r.get_full_name()}, вам пришел запрос на согласование документа :{document.description} от {sender_name}'
        message = MIMEText(message, 'plain')
        msg = MIMEMultipart()
        msg.attach(message)
        msg['From'] = sender_email
        msg['To'] = r.email
        msg['Subject'] = subject

        file_path = instance.document.file.path
        file_name = instance.document.file.name

        with open(file_path, 'rb') as file:
            attachment = MIMEApplication(file.read(), _subtype="pdf")
            attachment.add_header('Content-Disposition', f'attachment; filename="{file_name}"')
            msg.attach(attachment)

        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, r.email, msg.as_string())


