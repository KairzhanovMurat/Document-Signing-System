import os
import smtplib
import ssl
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pdfkit
import qrcode
from PIL import Image
from PyPDF2 import PdfWriter, PdfReader
from django.conf import settings

from . import models


def _generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    return img


def generate_pdf_with_qr(existing_pdf_path, output_pdf_path, header_content, table_data, qr_data):
    # Prepare the full HTML content for the new page
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body {{
      position: relative;
    }}

    table {{
      border-collapse: collapse;
      width: 100%;
    }}

    table, th, td {{
      border: 1px solid black;
    }}

    th, td {{
      padding: 8px;
      text-align: left;
    }}

    .header {{
      text-align: center;
      vertical-align: middle;
      margin-bottom: 20px;
    }}

    .signature {{
      text-align: center;
    }}

    .qr-code {{
      text-align: right;
    }}

    </style>
    </head>
    <body>

    <div class="header">
      {header_content}
    </div>

    <table>
    """

    for row in table_data:
        html_row = "<tr>"
        for cell in row:
            if cell.endswith(".png"):
                img_abs_path = os.path.abspath(cell)
                html_row += f'<td class="signature"><img src="{img_abs_path}" alt="Подпись" width="100"></td>'
            else:
                html_row += f"<td>{cell}</td>"
        html_row += "</tr>"
        full_html += html_row

    # Add a new row for the QR code
    full_html += """
    <tr>
      <td colspan="{0}" class="qr-code">
    """.format(len(table_data[0]))  # Calculate the number of columns in the table

    qr_code_img = _generate_qr_code(qr_data)
    qr_code_img_path = "qr_code.png"
    qr_code_img.save(qr_code_img_path)

    qr_code_abs_path = os.path.abspath(qr_code_img_path)
    full_html += f'<img src="{qr_code_abs_path}" alt="QR Code" width="250" height="250">'
    full_html += """
      </td>
    </tr>
    </table>
    """

    # Generate the PDF for the new page
    new_page_pdf_path = "new_page.pdf"
    options = {
        "page-size": "Letter",
        "encoding": "UTF-8",
        "no-outline": None
    }
    pdfkit.from_string(full_html, new_page_pdf_path, options=options)

    # Merge the new page PDF with the existing PDF
    existing_pdf = PdfReader(open(existing_pdf_path, "rb"))
    new_page_pdf = PdfReader(open(new_page_pdf_path, "rb"))

    output_pdf = PdfWriter()

    # Add existing pages
    for page_num in range(len(existing_pdf.pages)):
        page = existing_pdf.pages[page_num]
        output_pdf.add_page(page)

    # Add new page at the end
    for page_num in range(len(new_page_pdf.pages)):
        page = new_page_pdf.pages[page_num]
        output_pdf.add_page(page)

    # Save the output PDF
    with open(output_pdf_path, "wb") as output_file:
        output_pdf.write(output_file)

    # Remove temporary files
    os.remove(new_page_pdf_path)
    os.remove(qr_code_img_path)


def get_approval_data_dict(request_id):
    approval_data_dict = []

    approval_data_instances = models.UserApprovalData.objects.filter(approval_request_id=request_id).all()

    for instance in approval_data_instances:
        data = {
            'sender': instance.approval_request.sender.get_full_name(),
            'receiver': instance.user.get_full_name(),
            'approval_request': instance.approval_request.document.description,
            'browser': instance.browser,
            'ip_address': instance.ip_address,
            'approval_time': instance.approval_time.strftime('%Y-%m-%d %H:%M:%S %Z'),
        }
        approval_data_dict.append(data)

    return approval_data_dict


def optimize_png(input_path):
    try:
        with Image.open(input_path) as img:
            grayscale_img = img.convert('L')
            threshold = 128
            mask = grayscale_img.point(lambda p: p < threshold and 255)

            bbox = mask.getbbox()

            if bbox is None:
                print("No black pixels found. Image is empty.")
                return

            cropped_img = img.crop(bbox)

            cropped_img.save(input_path, "PNG")
    except Exception as e:
        print(f"Error optimizing PNG: {str(e)}")


def get_table_data(sender, request_id):
    optimize_png(sender.sign_image.path)
    data = [["№", "Наименование отдела", "ФИО", "Подпись"],
            ["1", sender.job_position, sender.get_initials(), sender.sign_image.path]]
    receivers = models.RequestReceivers.objects.filter(request_id=request_id)
    for idx, user in enumerate(receivers):
        optimize_png(user.receivers.sign_image.path)
        usr_data = [str(idx + 2), user.receivers.job_position, user.receivers.get_initials(),
                    user.receivers.sign_image.path]
        data.append(usr_data)
    return data


def send_success_email(receiver: models.DefaultUser, document: models.Document):
    subject = f'Документ согласован.'

    port = settings.EMAIL_PORT
    smtp_server = settings.EMAIL_HOST
    sender_email = settings.EMAIL_HOST_USER
    password = settings.EMAIL_HOST_PASSWORD
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    message = (
        f"""Дорогой/ая {receiver.get_full_name()}, ваш документ "{document.description}" успешно согласован.""")
    message = MIMEText(message, 'plain')
    msg = MIMEMultipart()
    msg.attach(message)
    msg['From'] = sender_email
    msg['To'] = receiver.email
    msg['Subject'] = subject

    file_path = document.file.path
    file_name = document.file.name

    with open(file_path, 'rb') as file:
        attachment = MIMEApplication(file.read(), _subtype="pdf")
        attachment.add_header('Content-Disposition', f'attachment; filename="{file_name}"')
        msg.attach(attachment)

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver.email, msg.as_string())
