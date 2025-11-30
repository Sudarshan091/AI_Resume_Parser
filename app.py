import os
import re
import pdfplumber
from flask import Flask, render_template, request

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def extract_data(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    # --- REGEX PATTERNS ---
    # 1. Extract Email
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email_match = re.search(email_pattern, text)
    email = email_match.group(0) if email_match else "Not Found"

    # 2. Extract Phone (Matches +91, 10-digit, etc.)
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}'
    phone_match = re.search(phone_pattern, text)
    phone = phone_match.group(0) if phone_match else "Not Found"

    # 3. Extract Name (Heuristic: First non-empty line)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    name = lines[0] if lines else "Not Found"

    return name, email, phone


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        if 'resume' not in request.files:
            return "No file uploaded", 400

        file = request.files['resume']
        if file.filename == '':
            return "No selected file", 400

        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Extract data
            try:
                name, email, phone = extract_data(filepath)
                result = True
            except Exception as e:
                name, email, phone = "Error", str(e), "Error"
                result = True

            # Clean up: Remove file after processing
            os.remove(filepath)

            return render_template("upload.html",
                                   name=name,
                                   email=email,
                                   phone=phone,
                                   result=result)

    return render_template("upload.html", result=False)


if __name__ == "__main__":
    app.run(debug=True)