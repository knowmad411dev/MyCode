import os
import re
from pathlib import Path
from difflib import SequenceMatcher

# Paths
SNIPPETS_PATH = Path(r"C:\Users\toddk\Documents\MyBrain\Snippets")
NOTES_PATH = Path(r"C:\Users\toddk\Documents\MyBrain")

# Regex to find code blocks in notes
CODE_BLOCK_REGEX = re.compile(r"```([a-zA-Z]*)\n(.*?)```", re.DOTALL)
# Regex to extract snippet embed links
SNIPPET_LINK_REGEX = re.compile(r"!\[\[Snippets/(.*?)\]\]")

SIMILARITY_THRESHOLD = 0.8  # Threshold for snippet similarity

def extract_code(snippet_path):
    """Extract code content from a snippet file."""
    with open(snippet_path, "r", encoding="utf-8") as file:
        content = file.read()
        match = CODE_BLOCK_REGEX.search(content)
        if match:
            return match.group(2).strip()
    return ""

def compare_code_with_snippets(code, snippet_files):
    """Compare a code block with all existing snippets."""
    for snippet_file in snippet_files:
        snippet_code = extract_code(snippet_file)
        similarity = SequenceMatcher(None, code, snippet_code).ratio()
        if similarity >= SIMILARITY_THRESHOLD:
            return snippet_file.name
    return None

def create_snippet(language, code, source_note, context=""):
    """Create a new snippet file with corrected metadata."""
    snippet_name = f"{language}_{hash(code)}.md"
    snippet_path = SNIPPETS_PATH / snippet_name

    metadata = (
        f"---\n"
        f"tags:\n"
        f"  - snippet\n"
        f"  - {language}\n"
        f"source-note: [[{source_note}]]\n"
        f"context: >\n"
        f"  {context}\n"
        f"---\n"
    )

    with open(snippet_path, "w", encoding="utf-8") as file:
        file.write(metadata)
        file.write(f"```{language}\n{code}\n```")

    return snippet_name

def process_note(note_path, snippet_files):
    """Process a single note to handle its code blocks."""
    with open(note_path, "r", encoding="utf-8") as file:
        content = file.read()

    updated_content = content
    for match in CODE_BLOCK_REGEX.finditer(content):
        language = match.group(1) or "plain"
        code = match.group(2).strip()

        # Extract surrounding text as context
        context_start = max(content.rfind("\n", 0, match.start()), 0)
        context_end = content.find("\n", match.end())
        context = content[context_start:context_end].strip()

        # Check if a similar snippet already exists
        existing_snippet = compare_code_with_snippets(code, snippet_files)

        if existing_snippet:
            # Replace code block with an embed link to the existing snippet
            embed_link = f"![[Snippets/{existing_snippet}]]"
        else:
            # Create a new snippet and replace the code block
            snippet_name = create_snippet(language, code, note_path.name, context)
            embed_link = f"![[Snippets/{snippet_name}]]"

            # Add the new snippet to the list of snippet files
            snippet_files.append(SNIPPETS_PATH / snippet_name)

        # Replace the code block in the note with the embed link
        updated_content = updated_content.replace(match.group(0), embed_link)

    # Save the updated note
    with open(note_path, "w", encoding="utf-8") as file:
        file.write(updated_content)

def main():
    # Ensure the Snippets folder exists
    if not SNIPPETS_PATH.exists():
        SNIPPETS_PATH.mkdir(parents=True)

    # Load all existing snippet files
    snippet_files = list(SNIPPETS_PATH.glob("*.md"))

    # Process all notes for new code blocks
    for note_path in NOTES_PATH.rglob("*.md"):
        with open(note_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Skip notes that already have snippet embed links
        if SNIPPET_LINK_REGEX.search(content):
            continue

        print(f"Processing note: {note_path}")
        process_note(note_path, snippet_files)

    print("Finished processing notes.")

if __name__ == "__main__":
    main()
