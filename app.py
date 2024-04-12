from flask import Flask, request, jsonify, send_from_directory
import PyPDF2

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    try:
        pdf_file = request.files['pdf']
        reader = PyPDF2.PdfReader(pdf_file)
        fields = reader.get_fields()
        field_names = list(fields.keys()) if fields else []
        return jsonify({'fields': field_names})
    except Exception as e:
        # Returning the error details or type can help debug
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
