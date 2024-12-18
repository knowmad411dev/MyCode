import os
import re
import json
from pathlib import Path
from difflib import SequenceMatcher
from markdown_it import MarkdownIt

# Paths
VAULT_PATH = r"C:\Users\toddk\Documents\MyBrain"
IGNORE_FOLDERS = {"Attachments", "Templates", "Prompting", "Journal"}
OUTPUT_FOLDER = Path(VAULT_PATH) / "Snippets"
REPORT_PATH = Path(r"C:\Users\toddk\Documents\deduplication_report.txt")
PROGRESS_FILE = Path(r"C:\Users\toddk\Documents\deduplication_progress.json")
BACKUP_FOLDER = Path(VAULT_PATH) / "Backup"

# Regex patterns
CODE_BLOCK_REGEX = re.compile(r"```.*?\n(.*?)```", re.DOTALL)
SNIPPET_LINK_REGEX = re.compile(r"!\[\[Snippets/(.*?)\]\]")
YAML_REGEX = re.compile(r"---(.*?)---", re.DOTALL)
FILENAME_PATTERN = re.compile(r"^\w+_[-\d]+\.md$")

# Thresholds
SIMILARITY_THRESHOLD = 0.8
SIMILARITY_THRESHOLD_DEDUP = 1.00
SIMILARITY_THRESHOLD_REPORT = 0.90

# Ensure output and backup folders exist
OUTPUT_FOLDER.mkdir(exist_ok=True)
BACKUP_FOLDER.mkdir(exist_ok=True)

def backup_file(file_path):
    """Backup a file before making changes."""
    backup_path = BACKUP_FOLDER / file_path.name
    with open(file_path, "r", encoding="utf-8") as src, open(backup_path, "w", encoding="utf-8") as dst:
        dst.write(src.read())
    print(f"Backup created for: {file_path}")

def extract_snippets_and_replace(note_path, relative_path):
    """Extract code snippets from a note, save them as snippets, and replace with embed links."""
    backup_file(note_path)
    with open(note_path, "r", encoding="utf-8") as file:
        content = file.read()

    md = MarkdownIt()
    tokens = md.parse(content)
    snippets = []
    updated_content = content

    for i, token in enumerate(tokens):
        if token.type == "fence":
            language = token.info or "plaintext"
            code = token.content.strip()

            # Capture context (first 3 lines before the code block)
            context_lines = content[:token.map[0]].splitlines()[-3:]
            context = "\n".join(line.strip() for line in context_lines if line.strip())

            # Create a filename based on the snippet's language and hash of its content
            file_name = f"{language}_{hash(code)}.md"
            snippet_path = OUTPUT_FOLDER / file_name

            # Check if the snippet file already exists
            if snippet_path.exists():
                # Append the source note to the existing snippet file
                with open(snippet_path, "a", encoding="utf-8") as snippet_file:
                    snippet_file.write(f"source-note: [[{relative_path}]]\n")
            else:
                # Save the snippet
                with open(snippet_path, "w", encoding="utf-8") as snippet_file:
                    snippet_file.write(f"---\n")
                    snippet_file.write(f"tags: [snippet, {language}]\n")
                    snippet_file.write(f"source-note: [[{relative_path}]]\n")
                    snippet_file.write(f"context: |\n  {context}\n")
                    snippet_file.write(f"---\n\n")
                    snippet_file.write(f"```{language}\n{code}\n```\n")

            # Verify that the snippet file was created successfully
            if snippet_path.exists():
                # Replace the code block in the note with an embed link as a comment
                embed_link = f"<!-- ![[Snippets/{file_name.replace(os.sep, '/')}]] -->"
                updated_content = updated_content.replace(token.markup + token.info + "\n" + token.content + token.markup, f"{embed_link}\n```{language}\n{code}\n```", 1)
            else:
                print(f"Error: Failed to create snippet file {snippet_path}")

    # Write the updated note content back to the original file
    with open(note_path, "w", encoding="utf-8") as file:
        file.write(updated_content)

    return snippets

def scan_vault():
    """Scan the vault for Markdown files and extract code snippets."""
    all_snippets = []

    for root, dirs, files in os.walk(VAULT_PATH):
        # Skip ignored folders
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in IGNORE_FOLDERS]

        for file in files:
            if file.endswith(".md"):
                note_path = Path(root) / file
                relative_path = os.path.relpath(note_path, VAULT_PATH)
                snippets = extract_snippets_and_replace(note_path, relative_path)
                all_snippets.extend(snippets)

    return all_snippets

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
                similar_pairs.append((snippet_files[i], snippet_files[j], similarity))
    return similar_pairs

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
    for note_path in Path(VAULT_PATH).rglob("*.md"):
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

def fix_snippet_metadata(snippet_path):
    """Correct the YAML metadata in a snippet file."""
    with open(snippet_path, "r", encoding="utf-8") as file:
        content = file.read()
        yaml_match = YAML_REGEX.search(content)
        code_match = CODE_BLOCK_REGEX.search(content)

        metadata = yaml_match.group(1).strip() if yaml_match else ""
        code = code_match.group(1).strip() if code_match else ""

    # Parse existing metadata
    tags = []
    source_note = ""
    context = ""
    
    if metadata:
        for line in metadata.splitlines():
            if line.startswith("tags:"):
                tags = [tag.strip() for tag in line.replace("tags:", "").split(",")]
            elif line.startswith("source-note:"):
                source_note = line.replace("source-note:", "").strip()
            elif line.startswith("context:"):
                context = line.replace("context:", "").strip()

    # Correct the metadata format
    corrected_metadata = (
        f"---\n"
        f"tags:\n"
        f"  - snippet\n"
        f"  - {tags[1] if len(tags) > 1 else 'unknown'}\n"
        f"source-note: {source_note if source_note else '[[unknown note]]'}\n"
        f"context: >\n"
        f"  {context if context else 'No context available.'}\n"
        f"---\n"
    )

    # Write back corrected metadata and code to the snippet file
    with open(snippet_path, "w", encoding="utf-8") as file:
        file.write(corrected_metadata)
        file.write(f"```{tags[1] if len(tags) > 1 else 'plain'}\n{code}\n```")

    print(f"Fixed metadata for: {snippet_path}")

def main():
    """Main function to manage snippets."""
    print("Scanning vault for code snippets...")
    snippets = scan_vault()
    print(f"Found {len(snippets)} snippets. Processing...")

    # Load all existing snippet files
    snippet_files = list(OUTPUT_FOLDER.glob("*.md"))
    if not snippet_files:
        print("No snippet files found.")
        return

    # Load progress
    processed_snippets = load_progress()

    # Compare snippets for similarity
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
                snippet_mapping[snippet_b.name] = snippet_a.name
            elif SIMILARITY_THRESHOLD_REPORT <= similarity < SIMILARITY_THRESHOLD_DEDUP:
                similar_pairs.append((snippet_a.name, snippet_b.name, similarity))

        processed_snippets.add(snippet_a.name)
        save_progress(processed_snippets)

        if (i + 1) % 10 == 0 or i + 1 == total_snippets:
            print(f"Processed {i + 1}/{total_snippets} snippets...")

    # Update notes with deduplicated snippets
    update_notes(snippet_mapping)

    # Delete duplicate snippet files
    for duplicate in snippet_mapping.keys():
        duplicate_path = OUTPUT_FOLDER / duplicate
        if duplicate_path.exists():
            print(f"Deleting duplicate snippet: {duplicate}")
            duplicate_path.unlink()

    # Generate report for high similarity pairs
    with open(REPORT_PATH, "w", encoding="utf-8") as report_file:
        report_file.write("Snippets with 90-99% similarity:\n\n")
        for snippet_a, snippet_b, similarity in similar_pairs:
            if SIMILARITY_THRESHOLD_REPORT <= similarity < SIMILARITY_THRESHOLD_DEDUP:
                report_file.write(f"{snippet_a} and {snippet_b} (Similarity: {similarity:.2f})\n")

    print("Deduplication complete. Report saved at:", REPORT_PATH)

    # Fix metadata for all snippets
    for snippet_path in OUTPUT_FOLDER.glob("*.md"):
        fix_snippet_metadata(snippet_path)

    print("Finished processing snippets.")

if __name__ == "__main__":
    main()
