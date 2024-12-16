import os
import re
from pathlib import Path
from difflib import SequenceMatcher

# Path to the Snippets folder
SNIPPETS_PATH = Path(r"C:\Users\toddk\Documents\MyBrain\Snippets")
SIMILARITY_THRESHOLD = 0.8  # Adjust this threshold as needed (0.8 = 80% similar)

# Regex to extract code content from snippet files
CODE_BLOCK_REGEX = re.compile(r"```.*?\n(.*?)```", re.DOTALL)

# Regex to match filenames with the pattern: language_<hash>.md
FILENAME_PATTERN = re.compile(r"^\w+_[-\d]+\.md$")


def extract_code(snippet_path):
    """Extract code content from a snippet file."""
    with open(snippet_path, "r", encoding="utf-8") as file:
        content = file.read()
        match = CODE_BLOCK_REGEX.search(content)
        if match:
            return match.group(1).strip()
    return ""


def compare_snippets(snippet_files):
    """Compare all snippets for similarity and return pairs of similar files."""
    similar_pairs = []

    for i in range(len(snippet_files)):
        code_a = extract_code(snippet_files[i])
        for j in range(i + 1, len(snippet_files)):
            code_b = extract_code(snippet_files[j])
            similarity = SequenceMatcher(None, code_a, code_b).ratio()
            if similarity >= SIMILARITY_THRESHOLD:
                similar_pairs.append((
                    snippet_files[i],
                    snippet_files[j],
                    similarity
                ))
    return similar_pairs


def main():
    # Ensure the Snippets folder exists
    if not SNIPPETS_PATH.exists():
        print(f"Error: The directory {SNIPPETS_PATH} does not exist.")
        return

    print(f"Directory exists: {SNIPPETS_PATH}")
    print("Contents:", list(SNIPPETS_PATH.iterdir()))

    # Get all snippet files matching the pattern
    snippet_files = [f for f in SNIPPETS_PATH.iterdir() if FILENAME_PATTERN.match(f.name)]
    print("Matching files:", [f.name for f in snippet_files])

    if not snippet_files:
        print("No snippet files found.")
        return

    print(f"Found {len(snippet_files)} snippet files. Comparing for similarity...")
    similar_pairs = compare_snippets(snippet_files)

    # Output similar pairs
    if similar_pairs:
        print(f"Found {len(similar_pairs)} similar snippet pairs:")
        for file_a, file_b, similarity in similar_pairs:
            print(f"- {file_a.name} and {file_b.name} (Similarity: {similarity:.2f})")
    else:
        print("No similar snippets found.")


if __name__ == "__main__":
    main()
