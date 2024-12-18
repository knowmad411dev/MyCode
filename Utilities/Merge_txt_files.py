import os
import chardet  # Install this with `pip install chardet`
import re

def detect_file_encoding(file_path):
    """Detect the encoding of a file."""
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        return result['encoding']

def is_valid_line(line):
    """
    Check if a line is valid:
    - Exclude lines containing a dot (.) or any number (0-9).
    """
    return not re.search(r"[0-9\.]", line)

def read_and_filter_lines(file_path):
    """
    Read lines from a file and filter invalid lines.
    
    :param file_path: The path to the file to read.
    :return: A list of valid lines.
    """
    encoding = detect_file_encoding(file_path)
    print(f"Encoding for {file_path}: {encoding}")
    
    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as file:
            lines = file.read().splitlines()
        valid_lines = [line for line in lines if is_valid_line(line)]
        return valid_lines
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def merge_and_save_files(input_file1, input_file2, output_file):
    """
    Merge two files, filter invalid lines, and save sorted lines to an output file.
    
    :param input_file1: The path to the first input file.
    :param input_file2: The path to the second input file.
    :param output_file: The path to the output file.
    """
    # Read and filter lines from both input files
    lines1 = read_and_filter_lines(input_file1)
    lines2 = read_and_filter_lines(input_file2)

    # Merge all lines
    all_lines = set(lines1 + lines2)
    print(f"Total lines before filtering: {len(all_lines)}")  # Debugging

    # Sort the valid lines case-insensitively
    sorted_lines = sorted(all_lines, key=lambda line: line.lower())

    print(f"\nTotal valid lines after filtering: {len(sorted_lines)}")

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")

    # Write the sorted lines to the output file
    if sorted_lines:
        try:
            with open(output_file, 'w', encoding='utf-8') as outfile:
                outfile.write('\n'.join(sorted_lines))
            print(f"\nFiles merged and saved to {output_file}")
        except Exception as e:
            print(f"Error writing to {output_file}: {e}")
    else:
        print("No valid lines found. File was not created.")

# File paths
input_file1 = r"C:\Users\toddk\Documents\The_Oxford_5000_cleaned.txt"
input_file2 = r"C:\Users\toddk\Documents\The_Oxford_3000_cleaned.txt"
output_file = r"C:\Users\toddk\Documents\Oxford_5000_common_word.txt"

# Merge and save files
merge_and_save_files(input_file1, input_file2, output_file)
