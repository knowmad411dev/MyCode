import os
import re

def scan_directory_for_imports(root_dir, output_file):
    """
    Scans the given directory and its subdirectories for Python files,
    extracts import statements, and writes them to an output file.

    :param root_dir: The root directory to start scanning
    :param output_file: The path to the output file where imports will be saved
    """
    imports = set()  # Use a set to avoid duplicate imports

    for root, dirs, files in os.walk(root_dir):
        # Filter out directories and files starting with "."
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        files = [f for f in files if not f.startswith('.') and f.endswith('.py')]

        for file in files:
            full_path = os.path.join(root, file)
            with open(full_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # Match import and from-import statements
                    match = re.match(r'^\s*(import\s+\w+|from\s+\w+\s+import\s+.+)', line)
                    if match:
                        imports.add(match.group(0).strip())

    # Write the collected imports to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        for imp in sorted(imports):  # Sort imports alphabetically for readability
            f.write(f"{imp}\n")

    print(f"Imports written to {output_file}")


if __name__ == "__main__":
    root_directory = r"C:\Users\toddk\Documents\MyCode"
    output_file_path = r"C:\Users\toddk\Documents\MyCode\import_list.txt"
    
    scan_directory_for_imports(root_directory, output_file_path)
