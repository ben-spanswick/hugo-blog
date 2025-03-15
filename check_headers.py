import os
import yaml
import re

# Path to the Hugo content directory
CONTENT_DIR = "/mnt/blog/content"

# Required front matter fields
REQUIRED_FIELDS = ["title", "date", "draft"]

def check_front_matter(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Ensure file starts and ends with ---
    if len(lines) < 2 or not (lines[0].strip() == "---" and "---" in lines[1:]):
        print(f"❌ ERROR: {file_path} - Missing or improperly formatted front matter delimiters.")
        return
    
    # Extract front matter content
    front_matter = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        front_matter.append(line)
    
    # Parse YAML front matter
    try:
        metadata = yaml.safe_load("".join(front_matter))
    except yaml.YAMLError as e:
        print(f"❌ ERROR: {file_path} - Invalid YAML syntax: {e}")
        return
    
    # Check for missing required fields
    for field in REQUIRED_FIELDS:
        if field not in metadata:
            print(f"⚠️ WARNING: {file_path} - Missing required field: {field}")
    
    # Validate date format
    if "date" in metadata:
        if not re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", str(metadata["date"])):
            print(f"⚠️ WARNING: {file_path} - Incorrect date format (expected ISO 8601)")

def scan_markdown_files():
    for root, _, files in os.walk(CONTENT_DIR):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                check_front_matter(file_path)

if __name__ == "__main__":
    print("🔍 Scanning Markdown files for front matter issues...\n")
    scan_markdown_files()
    print("\n✅ Scan complete.")
