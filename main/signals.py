import os
from django.db.models.signals import pre_delete, post_save
from django.dispatch.dispatcher import receiver
from .models import Document, ApprovalRequest
from django.core.mail import EmailMessage, get_connection


@receiver(pre_delete, sender=Document)
def delete_document_file(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(post_save, sender=ApprovalRequest)
def send_approval_request_email(sender, instance, **kwargs):
    # receivers = instance.receivers.all()
    # document = instance.document
    # sender_email = instance.sender.email  # Get the email of the user who created the request
    #
    # subject = f'Approval Request for Document: {document.description}'
    # message = f'You have received an approval request for the document: {document.description}'
    #
    # # Provided email credentials
    # from_email = 'M.Kairzhanov@dss.kz'  # Your email address
    # email_password = '8n0w942'  # Your email password
    #
    # smtp_server = 'dssmail.dss.kz'
    # smtp_port = 465
    #
    # for receiver in receivers:
    #     recipient_list = [receiver.email]
    #
    #     email = EmailMessage(subject, message, from_email, recipient_list)
    #     email.attach_file(document.file.path)  # Attach the file to the email
    #
    #     # Configure the SMTP settings for sending email
    #     email.connection = get_connection(
    #         host=smtp_server,
    #         port=smtp_port,
    #         username=from_email,
    #         password=email_password,
    #         use_ssl=True,
    #     )
    #
    #     email.send()
    # print('test signal')
    ...


@receiver(post_save, sender=ApprovalRequest)
def send_approval_request_app(sender, instance, **kwargs):
    ...
