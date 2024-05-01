from flask import Flask, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes and origins

@app.route('/form.pdf')
def form_pdf():
    # Ensure the PDF file is in the same directory as this script, or specify the correct path
    return send_from_directory('.', 'form.pdf', as_attachment=True)

if __name__ == '__main__':
    app.run(port=8000)
