import io
import qrcode
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def sign_pdf_with_single_qr_code(pdf_path, output_path, full_names_and_signs, approval_data_dict):
    signature_width = 100  # Adjust as needed
    signature_height = 50
    qr_code_size = 170  # Adjust as needed

    # Load the existing PDF using PyPDF2
    existing_pdf = PdfReader(pdf_path)

    # Create a new PDF with PdfWriter
    new_pdf = PdfWriter()

    # Add all pages from the existing PDF to the new PDF
    for page_num in range(len(existing_pdf.pages)):
        new_pdf.add_page(existing_pdf.pages[page_num])

    # Create a new canvas for the last page
    last_page_overlay = io.BytesIO()
    last_page_canvas = canvas.Canvas(last_page_overlay, pagesize=letter)

    # Calculate the starting position for the list of names and signatures
    list_x = 100
    list_y = 300
    line_height = 60  # Adjust as needed

    # Draw the list of names and signatures on the last page
    for name, signature_path in full_names_and_signs:
        # Load and process the signature image
        signature_img = Image.open(signature_path)
        signature_img = signature_img.convert("RGBA")
        signature_img_with_white_bg = Image.new("RGBA", signature_img.size, (255, 255, 255))
        signature_img_with_white_bg.paste(signature_img, (0, 0), signature_img)
        signature_buffer = io.BytesIO()
        signature_img_with_white_bg.save(signature_buffer, format="PNG")
        signature_img_reader = ImageReader(signature_buffer)

        # Draw the full name
        last_page_canvas.drawString(
            list_x, list_y + signature_height / 2, f"{name}:"
        )

        # Draw the signature image
        last_page_canvas.drawImage(
            signature_img_reader, x=list_x + 120, y=list_y - 0, width=signature_width, height=signature_height
        )
        list_y -= line_height

    # Generate a QR code from approval_data_dict
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(str(approval_data_dict))  # Convert dict to string
    qr.make(fit=True)

    # Create an image of the QR code
    qr_image = qr.make_image(fill_color="black", back_color="white")

    # Save the QR code image to a buffer
    qr_image_buffer = io.BytesIO()
    qr_image.save(qr_image_buffer)
    qr_image_buffer.seek(0)  # Reset the buffer position

    qr_image_reader = ImageReader(qr_image_buffer)

    # Calculate coordinates for placing QR code on the right-bottom corner
    page_width, page_height = letter
    qr_x = page_width - qr_code_size - 50  # Adjust as needed
    qr_y = 50  # Adjust as needed

    # Draw the QR code image
    last_page_canvas.drawImage(
        qr_image_reader, x=qr_x, y=qr_y, width=qr_code_size, height=qr_code_size
    )

    last_page_canvas.save()

    # Merge the overlay with the last page
    last_page_overlay.seek(0)
    last_page_overlay_page = PdfReader(last_page_overlay)
    last_page = last_page_overlay_page.pages[0]

    # Add the modified last page to the new PDF
    new_pdf.add_page(last_page)

    # Save the modified PDF to the output path
    with open(output_path, "wb") as output_file:
        new_pdf.write(output_file)


from .models import UserApprovalData


def get_approval_data_dict(request_id):
    approval_data_dict = []

    approval_data_instances = UserApprovalData.objects.filter(approval_request_id=request_id).all()

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
