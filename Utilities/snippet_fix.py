import os
import re
from pathlib import Path

# Paths
SNIPPETS_PATH = Path(r"C:\Users\toddk\Documents\MyBrain\Snippets")

# Regex to extract YAML metadata and code block from snippet files
YAML_REGEX = re.compile(r"---(.*?)---", re.DOTALL)
CODE_BLOCK_REGEX = re.compile(r"```.*?\n(.*?)```", re.DOTALL)


def extract_metadata_and_code(snippet_path):
    """Extract metadata and code from a snippet file."""
    with open(snippet_path, "r", encoding="utf-8") as file:
        content = file.read()
        yaml_match = YAML_REGEX.search(content)
        code_match = CODE_BLOCK_REGEX.search(content)

        metadata = yaml_match.group(1).strip() if yaml_match else ""
        code = code_match.group(1).strip() if code_match else ""
        return metadata, code


def fix_snippet_metadata(snippet_path):
    """Correct the YAML metadata in a snippet file."""
    metadata, code = extract_metadata_and_code(snippet_path)

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
    # Ensure the Snippets folder exists
    if not SNIPPETS_PATH.exists():
        print(f"Error: The directory {SNIPPETS_PATH} does not exist.")
        return

    # Process all snippet files
    for snippet_path in SNIPPETS_PATH.glob("*.md"):
        print(f"Processing snippet: {snippet_path}")
        fix_snippet_metadata(snippet_path)

    print("Finished fixing snippet metadata.")


if __name__ == "__main__":
    main()
