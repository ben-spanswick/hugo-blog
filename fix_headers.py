import os
import yaml

# Define the base content directory
CONTENT_DIR = "/mnt/blog/content"

# Default front matter template
DEFAULT_FRONT_MATTER = {
    "title": "Untitled",
    "date": "2025-03-15T00:00:00Z",
    "draft": False
}

def has_valid_front_matter(lines):
    """Check if a file has correctly formatted front matter."""
    return len(lines) > 1 and lines[0].strip() == "---" and "---" in lines[1:]

def fix_markdown_file(file_path):
    """Fix front matter for a given Markdown file."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # If front matter is missing or malformed, fix it
    if not has_valid_front_matter(lines):
        print(f"🛠 Fixing: {file_path}")

        # Extract existing content (if any)
        content_start = 0
        if "---" in lines:
            content_start = lines.index("---\n", 1) + 1  # Find end of broken front matter

        content = "".join(lines[content_start:]).strip()

        # Generate valid YAML front matter
        new_front_matter = "---\n" + yaml.dump(DEFAULT_FRONT_MATTER, default_flow_style=False) + "---\n\n"

        # Write back the corrected content
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_front_matter + content + "\n")

        print(f"✅ Fixed: {file_path}")

def scan_and_fix():
    """Scan all Markdown files in the content directory and fix their front matter."""
    print("🔍 Scanning and fixing front matter issues...\n")

    for root, _, files in os.walk(CONTENT_DIR):
        for file in files:
            if file.endswith(".md"):
                fix_markdown_file(os.path.join(root, file))

    print("\n✅ Scan and fix complete.")

if __name__ == "__main__":
    scan_and_fix()
