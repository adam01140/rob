from flask import Flask, request, jsonify, send_from_directory, send_file
import PyPDF2
from PyPDF2 import PdfWriter

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
        return jsonify({'error': str(e)}), 500

@app.route('/edit_field', methods=['POST'])
def edit_field():
    try:
        field_name = request.form['fieldName']
        field_value = request.form['fieldValue']
        pdf_file = request.files['pdf']
        reader = PyPDF2.PdfReader(pdf_file)
        writer = PdfWriter()

        # Copy pages and modify the fields
        for page in reader.pages:
            page[PyPDF2.generic.NameObject('/Annots')] = PyPDF2.generic.ArrayObject()
            for annot in page['/Annots']:
                if annot.get('/T') == field_name:
                    annot.update({
                        PyPDF2.generic.NameObject('/V'): PyPDF2.generic.TextStringObject(field_value)
                    })
            writer.add_page(page)

        # Save the new PDF in memory
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)

        return send_file(output_stream, attachment_filename='modified_pdf.pdf', as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
