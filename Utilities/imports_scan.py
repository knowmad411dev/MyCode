import os
import re
from collections import defaultdict
import markdown  # Add markdown module

def extract_imports_from_file(file_path):
    """
    Extract import statements from a Python file.
    
    :param file_path: The path to the Python file.
    :return: A set of import statements.
    """
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Match import and from-import statements
                match = re.match(r'^\s*(import\s+\w+|from\s+\w+\s+import\s+.+)', line)
                if match:
                    imports.add(match.group(0).strip())
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return imports

def scan_directory_for_imports(root_dir):
    """
    Scans the given directory and its subdirectories for Python files,
    extracts import statements, and organizes them by folder and file.
    
    :param root_dir: The root directory to start scanning.
    :return: A dictionary where keys are folder paths and values are dictionaries
             with file names as keys and sets of import statements as values.
    """
    imports_by_folder_and_file = defaultdict(lambda: defaultdict(set))

    for root, dirs, files in os.walk(root_dir):
        # Filter out directories and files starting with "."
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        files = [f for f in files if not f.startswith('.') and f.endswith('.py')]

        for file in files:
            full_path = os.path.join(root, file)
            folder_path = os.path.relpath(root, root_dir)
            imports_by_folder_and_file[folder_path][file].update(extract_imports_from_file(full_path))

    return imports_by_folder_and_file

def write_imports_to_markdown(imports_by_folder_and_file, output_file):
    """
    Writes the collected import statements to a Markdown file, organized by folder and file.
    
    :param imports_by_folder_and_file: A dictionary where keys are folder paths and values are dictionaries
                                       with file names as keys and sets of import statements as values.
    :param output_file: The path to the output file where imports will be saved.
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for folder, files in sorted(imports_by_folder_and_file.items()):
                f.write(f"# Imports from folder: {folder}\n")
                for file, imports in sorted(files.items()):
                    f.write(f"## {file}\n")
                    for imp in sorted(imports):  # Sort imports alphabetically for readability
                        f.write(f"- `{imp}`\n")
                    f.write("\n")
        print(f"Markdown report written to {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")

if __name__ == "__main__":
    root_directory = r"C:\Users\toddk\Documents\MyCode"
    output_file_path = r"C:\Users\toddk\Documents\MyCode\import_list.md"  # Change to .md for Markdown
    
    imports_by_folder_and_file = scan_directory_for_imports(root_directory)
    write_imports_to_markdown(imports_by_folder_and_file, output_file_path)
