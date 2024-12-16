# Ensure this is done:  python -m pip install Pillow
# I could do this if I have many to convert:  mkdir webp_to_png cd webp_to_png

from PIL import Image
import os

# Define the directory to monitor
downloads_dir = "C:/Users/toddk/Downloads"
# Monitor for any .webp files
for filename in os.listdir(downloads_dir):
    if filename.endswith(".webp"):
        webp_path = os.path.join(downloads_dir, filename)
        png_path = webp_path.replace(".webp", ".png")

        # Open and convert .webp to .png

        with Image.open(webp_path) as img:
            img.save(png_path, "PNG")
        print(f"Converted {filename} to PNG format.")
