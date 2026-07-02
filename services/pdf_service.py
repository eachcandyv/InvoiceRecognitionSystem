import fitz
import os
import uuid

def pdf_to_image(pdf_path):
    output_folder = "static/uploads"
    os.makedirs(output_folder, exist_ok=True)

    doc = fitz.open(pdf_path)
    page = doc[0]

    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

    image_filename = f"pdf_{uuid.uuid4().hex}.png"
    image_path = os.path.join(output_folder, image_filename)

    pix.save(image_path)
    doc.close()

    return image_path