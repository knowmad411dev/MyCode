import os
import re
from pathlib import Path

# Path to your Obsidian vault
VAULT_PATH = r"C:\Users\toddk\Documents\MyBrain"
IGNORE_FOLDERS = {"Attachments", "Templates", "Prompting", "Journal"}
OUTPUT_FOLDER = Path(VAULT_PATH) / "Snippets"

# Ensure output folder exists
OUTPUT_FOLDER.mkdir(exist_ok=True)

# Regex to match code blocks
CODE_BLOCK_REGEX = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)


def extract_snippets_and_replace(note_path, relative_path):
    """Extract code snippets from a note, save them as snippets, and replace with embed links."""
    with open(note_path, "r", encoding="utf-8") as file:
        content = file.read()

    snippets = []
    updated_content = content
    for match in CODE_BLOCK_REGEX.finditer(content):
        language = match.group(1) or "plain"
        code = match.group(2).strip()

        # Capture context (first 3 lines before the code block)
        context_lines = content[:match.start()].splitlines()[-3:]
        context = "\n".join(line.strip() for line in context_lines if line.strip())

        # Create a filename based on the snippet's language and hash of its content
        file_name = f"{language}_{hash(code)}.md"
        snippet_path = OUTPUT_FOLDER / file_name

        # Save the snippet
        with open(snippet_path, "w", encoding="utf-8") as snippet_file:
            snippet_file.write(f"---\n")
            snippet_file.write(f"tags: [snippet, {language}]\n")
            snippet_file.write(f"source-note: [[{relative_path}]]\n")
            snippet_file.write(f"context: |\n  {context}\n")
            snippet_file.write(f"---\n\n")
            snippet_file.write(f"```{language}\n{code}\n```\n")

        # Add the snippet metadata to the list
        snippets.append({
            "language": language,
            "code": code,
            "context": context,
            "source": relative_path,
            "file_name": file_name
        })

        # Replace the code block in the note with an embed link
        embed_link = f"![[Snippets/{file_name}]]"
        updated_content = updated_content.replace(match.group(0), embed_link, 1)

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


def main():
    print("Scanning vault for code snippets...")
    snippets = scan_vault()
    print(f"Found {len(snippets)} snippets. Processed and updated notes successfully.")


if __name__ == "__main__":
    main()
