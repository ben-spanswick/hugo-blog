import os
import yaml
import re

# Define the base content directory
CONTENT_DIR = "/mnt/blog/content"

def clean_yaml_lines(lines):
    """Removes invalid YAML lines that might have Markdown formatting or code blocks."""
    cleaned_lines = []
    inside_code_block = False

    for line in lines:
        # Detect and ignore code block markers
        if line.strip().startswith("```"):
            inside_code_block = not inside_code_block
            continue

        # Ignore lines inside a code block
        if inside_code_block:
            continue

        # Ignore invalid list items with Markdown formatting like **bold**
        if re.match(r"^\s*-\s*\*\*.*\*\*", line):
            continue

        cleaned_lines.append(line)

    return cleaned_lines

def fix_front_matter(file_path):
    """Fixes YAML front matter in a Markdown file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.readlines()

    # Find front matter delimiters
    front_matter_indices = [i for i, line in enumerate(content) if line.strip() == "---"]
    
    if len(front_matter_indices) < 2:
        print(f"❌ No valid front matter in: {file_path}. Skipping...")
        return
    
    start, end = front_matter_indices[0], front_matter_indices[1]
    raw_front_matter = content[start + 1:end]
    cleaned_front_matter = clean_yaml_lines(raw_front_matter)

    try:
        front_matter_data = yaml.safe_load("\n".join(cleaned_front_matter)) or {}
    except yaml.YAMLError as e:
        print(f"❌ YAML Error in {file_path}: {e}. Skipping...")
        return

    # Ensure required fields exist
    front_matter_data.setdefault("title", "Untitled")
    front_matter_data.setdefault("date", "2025-03-15")  # Placeholder date
    front_matter_data.setdefault("tags", [])
    front_matter_data.setdefault("categories", [])
    front_matter_data.setdefault("draft", False)

    # Convert back to YAML format
    fixed_front_matter = yaml.dump(front_matter_data, default_flow_style=False)

    # Remove old front matter and insert the fixed version
    cleaned_content = "".join(content[end + 1:]).strip()
    final_content = f"---\n{fixed_front_matter}---\n\n{cleaned_content}"

    # Write back the corrected file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_content)

    print(f"✅ Fixed: {file_path}")

# Walk through content directory and fix Markdown files
for root, _, files in os.walk(CONTENT_DIR):
    for file in files:
        if file.endswith(".md"):
            fix_front_matter(os.path.join(root, file))

print("\n🚀 All front matter issues should now be fixed!")
