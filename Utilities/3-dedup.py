import os
import re
from pathlib import Path
from difflib import SequenceMatcher
import json

# Paths
SNIPPETS_PATH = Path(r"C:\Users\toddk\Documents\MyBrain\Snippets")
NOTES_PATH = Path(r"C:\Users\toddk\Documents\MyBrain")
REPORT_PATH = Path(r"C:\Users\toddk\Documents\deduplication_report.txt")
PROGRESS_FILE = Path(r"C:\Users\toddk\Documents\deduplication_progress.json")

# Regex to extract snippet embed links from notes
SNIPPET_LINK_REGEX = re.compile(r"!\[\[Snippets/(.*?)\]\]")

# Regex to extract code content from snippet files
CODE_BLOCK_REGEX = re.compile(r"```.*?\n(.*?)```", re.DOTALL)

# Thresholds
SIMILARITY_THRESHOLD_DEDUP = 1.00
SIMILARITY_THRESHOLD_REPORT = 0.90


def extract_code(snippet_path):
    """Extract code content from a snippet file."""
    with open(snippet_path, "r", encoding="utf-8") as file:
        content = file.read()
        match = CODE_BLOCK_REGEX.search(content)
        if match:
            return match.group(1).strip()
    return ""


def find_snippet_references(note_path, snippet_name):
    """Find all references to a snippet in a note."""
    with open(note_path, "r", encoding="utf-8") as file:
        content = file.read()
        return list(SNIPPET_LINK_REGEX.finditer(content)), content


def replace_snippet_references(note_path, old_snippet, new_snippet):
    """Replace references to an old snippet with a new snippet."""
    matches, content = find_snippet_references(note_path, old_snippet)
    if matches:
        updated_content = content.replace(f"![[Snippets/{old_snippet}]]", f"![[Snippets/{new_snippet}]]")
        with open(note_path, "w", encoding="utf-8") as file:
            file.write(updated_content)


def update_notes(snippet_mapping):
    """Update notes to replace old snippet references with new ones."""
    for note_path in NOTES_PATH.rglob("*.md"):
        for old_snippet, new_snippet in snippet_mapping.items():
            print(f"Updating note: {note_path} (Replacing {old_snippet} with {new_snippet})")
            replace_snippet_references(note_path, old_snippet, new_snippet)


def save_progress(processed_snippets):
    """Save progress to a JSON file."""
    with open(PROGRESS_FILE, "w", encoding="utf-8") as file:
        json.dump(list(processed_snippets), file)


def load_progress():
    """Load progress from a JSON file."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r", encoding="utf-8") as file:
            return set(json.load(file))
    return set()


def main():
    # Step 1: Gather all snippet files
    snippet_files = list(SNIPPETS_PATH.glob("*.md"))
    if not snippet_files:
        print("No snippet files found.")
        return

    # Load progress
    processed_snippets = load_progress()

    # Step 2: Compare snippets for similarity
    similar_pairs = []
    snippet_mapping = {}

    total_snippets = len(snippet_files)
    for i, snippet_a in enumerate(snippet_files):
        if snippet_a.name in processed_snippets:
            continue

        code_a = extract_code(snippet_a)
        for snippet_b in snippet_files[i + 1:]:
            code_b = extract_code(snippet_b)
            similarity = SequenceMatcher(None, code_a, code_b).ratio()

            if similarity >= SIMILARITY_THRESHOLD_DEDUP:
                similar_pairs.append((snippet_a.name, snippet_b.name, similarity))
                # Mark the duplicate for deduplication (keep snippet_a as primary)
                snippet_mapping[snippet_b.name] = snippet_a.name
            elif SIMILARITY_THRESHOLD_REPORT <= similarity < SIMILARITY_THRESHOLD_DEDUP:
                similar_pairs.append((snippet_a.name, snippet_b.name, similarity))

        # Save progress after processing each snippet
        processed_snippets.add(snippet_a.name)
        save_progress(processed_snippets)

        # Print progress
        if (i + 1) % 10 == 0 or i + 1 == total_snippets:
            print(f"Processed {i + 1}/{total_snippets} snippets...")

    # Step 3: Update notes
    update_notes(snippet_mapping)

    # Step 4: Delete duplicate snippet files
    for duplicate in snippet_mapping.keys():
        duplicate_path = SNIPPETS_PATH / duplicate
        if duplicate_path.exists():
            print(f"Deleting duplicate snippet: {duplicate}")
            duplicate_path.unlink()

    # Step 5: Generate report for high similarity pairs
    with open(REPORT_PATH, "w", encoding="utf-8") as report_file:
        report_file.write("Snippets with 90-99% similarity:\n\n")
        for snippet_a, snippet_b, similarity in similar_pairs:
            if SIMILARITY_THRESHOLD_REPORT <= similarity < SIMILARITY_THRESHOLD_DEDUP:
                report_file.write(f"{snippet_a} and {snippet_b} (Similarity: {similarity:.2f})\n")

    print("Deduplication complete. Report saved at:", REPORT_PATH)


if __name__ == "__main__":
    main()
