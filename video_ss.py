import os
import cv2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from tqdm import tqdm

def get_mp4_files(root_dir):
    """Recursively find all .mp4 files in the given directory."""
    mp4_files = []
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".mp4"):
                mp4_files.append(os.path.join(subdir, file))
    return mp4_files

def create_screenshots(video_path, output_dir):
    """Generate screenshots every 2 seconds from the video."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Failed to open video: {video_path}")
        return []

    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    screenshots = []
    count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if count % (frame_rate * 2) == 0:  # Every 2 seconds
            screenshot_path = os.path.join(output_dir, f"screenshot_{count}.jpg")
            cv2.imwrite(screenshot_path, frame)
            screenshots.append(screenshot_path)

        count += 1

    cap.release()
    return screenshots

def create_pdf_from_screenshots(screenshots, output_pdf):
    """Create a PDF from a list of screenshots."""
    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter

    for screenshot in screenshots:
        c.drawImage(screenshot, 0, 0, width, height)
        c.showPage()

    c.save()

def process_videos(root_dir):
    """Process all .mp4 files in the directory."""
    mp4_files = get_mp4_files(root_dir)

    with tqdm(total=len(mp4_files), desc="Total Progress") as overall_pbar:
        for video_path in mp4_files:
            video_dir = os.path.dirname(video_path)
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            output_pdf = os.path.join(video_dir, f"{video_name}.pdf")

            temp_screenshots_dir = os.path.join(video_dir, f"{video_name}_screenshots")
            os.makedirs(temp_screenshots_dir, exist_ok=True)

            screenshots = create_screenshots(video_path, temp_screenshots_dir)

            if screenshots:
                create_pdf_from_screenshots(screenshots, output_pdf)
            else:
                print(f"No screenshots generated for: {video_path}")

            # Cleanup temporary screenshots
            for screenshot in screenshots:
                os.remove(screenshot)
            os.rmdir(temp_screenshots_dir)

            overall_pbar.update(1)

if __name__ == "__main__":
    root_directory = input("Enter the root directory to search for .mp4 files: ")
    process_videos(root_directory)
