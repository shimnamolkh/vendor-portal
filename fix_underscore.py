"""
Quick fix script to add underscore escape handling to ollama_service.py
"""

file_path = r"c:\Users\ITS38\Desktop\vENDORPORTAL\finance\services\ollama_service.py"

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the specific line
old_line = "                if isinstance(output_str, str):\n                    output_str = output_str.replace('\\\\\\\\n', '\\n')"
new_line = "                if isinstance(output_str, str):\n                    # First, handle escaped underscores (Invoice\\_No -> Invoice_No)\n                    output_str = output_str.replace('\\\\_', '_')\n                    \n                    # Then handle escaped newlines and quotes\n                    output_str = output_str.replace('\\\\\\\\n', '\\n')"

if old_line in content:
    content = content.replace(old_line, new_line)
    print("✅ Found and replaced the line")
else:
    print("❌ Could not find the exact line to replace")
    print("Looking for alternative...")
    
    # Try alternative approach
    old_pattern = "if isinstance(output_str, str):\r\n                    output_str = output_str.replace"
    if old_pattern in content:
        # Insert the underscore handling before the first replace
        insert_text = "if isinstance(output_str, str):\r\n                    # First, handle escaped underscores (Invoice\\_No -> Invoice_No)\r\n                    output_str = output_str.replace('\\\\_', '_')\r\n                    \r\n                    # Then handle escaped newlines and quotes\r\n                    output_str = output_str.replace"
        content = content.replace(old_pattern, insert_text)
        print("✅ Used alternative replacement")

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ File updated successfully!")
