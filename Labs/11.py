import re

# Path to your Markdown file
file_path = "CITS5503_Template_Labs1-5.md"

# Desired width for the images
image_width = 300

# Read the Markdown file
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Regex to find Markdown image syntax like ![img_x.png](img_x.png)
markdown_img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'

# Replacement function to convert to HTML image tag with width
def replace_image(match):
    alt_text = match.group(1)
    img_path = match.group(2)
    return f'<img src="{img_path}" alt="{alt_text}" width="{image_width}">'

# Replace all Markdown image syntax with HTML image tag
new_content = re.sub(markdown_img_pattern, replace_image, content)

# Write the updated content back to a new file
new_file_path = "updated_" + file_path
with open(new_file_path, 'w', encoding='utf-8') as file:
    file.write(new_content)

print(f"Images in {file_path} have been resized and updated. Check {new_file_path}.")
