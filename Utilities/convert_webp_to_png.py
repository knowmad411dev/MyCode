"""
Utility to convert .webp files to .png format.

Usage:
    python convert_webp_to_png.py <input_dir> <output_dir>

Arguments:
    input_dir  - Directory to monitor for .webp files
    output_dir - Directory to save converted .png files

Ensure Pillow is installed:
    python -m pip install Pillow

Example:
    python convert_webp_to_png.py C:/Users/toddk/Downloads C:/Users/toddk/Downloads/converted
"""

from PIL import Image
import os
import argparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up argument parser
parser = argparse.ArgumentParser(description="Convert .webp files to .png format.")
parser.add_argument("input_dir", help="Directory to monitor for .webp files")
parser.add_argument("output_dir", help="Directory to save converted .png files")
args = parser.parse_args()

# Ensure output directory exists
os.makedirs(args.output_dir, exist_ok=True)

# Monitor for any .webp files
for filename in os.listdir(args.input_dir):
    if filename.endswith(".webp"):
        webp_path = os.path.join(args.input_dir, filename)
        png_path = os.path.join(args.output_dir, filename.replace(".webp", ".png"))

        # Check if the output file already exists
        if os.path.exists(png_path):
            logging.warning(f"{png_path} already exists. Skipping conversion.")
            continue

        try:
            # Open and convert .webp to .png
            with Image.open(webp_path) as img:
                img.save(png_path, "PNG")
            logging.info(f"Converted {filename} to PNG format.")
        except Exception as e:
            logging.error(f"Failed to convert {filename}: {e}")
