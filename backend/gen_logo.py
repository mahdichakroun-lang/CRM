"""Generate logo_base64.py from FRS_logo.jpg"""
import base64
import os

logo_path = os.path.join(os.path.dirname(__file__), "..", "FRS_logo.jpg")
output_path = os.path.join(os.path.dirname(__file__), "app", "shared", "logo_base64.py")

with open(logo_path, "rb") as f:
    data = f.read()

b64 = base64.b64encode(data).decode()

with open(output_path, "w") as f:
    f.write(f'# Auto-generated FRS logo as base64 for email templates\n')
    f.write(f'FRS_LOGO_BASE64 = "{b64}"\n')

print(f"Done! Logo ({len(data)} bytes) saved to {output_path}")
