import os

import pdfkit
import qrcode
from PyPDF2 import PdfWriter, PdfReader

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


import pdfkit
import qrcode
import os
from PyPDF2 import PdfWriter, PdfReader, PageObject

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
    .qr-code {{
      position: fixed;
      bottom: -800px;
      right: 0px; 
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

    full_html += """
    </table>

    <div class="qr-code">
    """

    qr_code_img = _generate_qr_code(qr_data)
    qr_code_img_path = "qr_code.png"
    qr_code_img.save(qr_code_img_path)

    qr_code_abs_path = os.path.abspath(qr_code_img_path)
    full_html += f'<img src="{qr_code_abs_path}" alt="QR Code" width="300" height="300">'
    full_html += """
    </div>

    </body>
    </html>
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
    existing_pdf = PdfReader(existing_pdf_path)
    new_page_pdf = PdfReader(new_page_pdf_path)

    output_pdf = PdfWriter()

    # Add existing pages
    for page in existing_pdf.pages:
        output_pdf.add_page(page)

    # Add new page at the end
    for page in new_page_pdf.pages:
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


def get_table_data(request_id):
    data = [["№", "Наименование отдела", "ФИО", "Подпись"], ]
    receivers = models.RequestReceivers.objects.filter(request_id=request_id)
    for idx, user in enumerate(receivers):
        usr_data = [str(idx + 1), user.receivers.job_position, user.receivers.get_initials(),
                    user.receivers.sign_image.path]
        data.append(usr_data)
    return data
