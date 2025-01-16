import os
from tqdm import tqdm
from pdf2image import convert_from_path
import imagehash
from PyPDF2 import PdfReader, PdfWriter

def identify_pages_to_delete(pdf_path, resize_to=(100, 100), threshold=90):
    """Identify page numbers to delete based on low-quality image comparisons."""
    pages = convert_from_path(pdf_path, dpi=150, fmt='jpeg', grayscale=True)  # Low DPI for fast processing
    hashes = []
    pages_to_delete = []

    for i, page in enumerate(pages):
        # Resize for comparison
        resized_page = page.resize(resize_to)
        current_hash = imagehash.dhash(resized_page)

        # Compare with the previous page hash
        if i > 0 and current_hash - hashes[-1] < (1 - threshold / 100) * len(current_hash.hash) ** 2:
            pages_to_delete.append(i + 1)  # Pages are 1-indexed in PDF tools
        else:
            hashes.append(current_hash)

    return pages_to_delete

def delete_pages_from_pdf(pdf_path, pages_to_delete):
    """Delete specific pages from the original PDF and save it at the same location."""
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages):
        if i + 1 not in pages_to_delete:  # Keep only pages not in the delete list
            writer.add_page(page)

    new_path = os.path.splitext(pdf_path)[0] + "_cleaned.pdf"

    with open(new_path, "wb") as f:
        writer.write(f)

def find_all_pdfs(root_dir):
    """Recursively find all PDF files in the given directory."""
    pdf_files = []
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".pdf"):
                pdf_files.append(os.path.join(subdir, file))
    return pdf_files

def process_pdf(pdf_dir, resize_to=(100, 100), threshold=90):
    """Process PDFs to remove duplicate pages."""
    pdf_files = find_all_pdfs(pdf_dir)

    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        # Step 1: Identify pages to delete
        pages_to_delete = identify_pages_to_delete(pdf_file, resize_to, threshold)

        # Step 2: Delete identified pages from the original PDF
        delete_pages_from_pdf(pdf_file, pages_to_delete)

if __name__ == "__main__":
    pdf_directory = input("Enter the root directory containing the PDFs: ")
    process_pdf(pdf_directory)