from flask import Flask, request, jsonify, send_from_directory, send_file
import PyPDF2
import io

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    try:
        pdf_file = request.files['pdf']
        reader = PyPDF2.PdfReader(pdf_file.stream)
        fields = reader.get_fields()
        field_names = [{'name': name, 'is_checkbox': field.get('/FT') == '/Btn', 'is_text': field.get('/FT') == '/Tx'} for name, field in fields.items()] if fields else []
        return jsonify({'fields': field_names})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/edit_pdf', methods=['POST'])
def edit_pdf():
    try:
        pdf_file = request.files['pdf']
        reader = PyPDF2.PdfReader(pdf_file.stream)
        writer = PyPDF2.PdfWriter()

        for page in reader.pages:
            if '/Annots' in page:
                annots = page['/Annots']
                for annot in annots:
                    resolved_annot = annot.get_object()
                    field_name = resolved_annot.get('/T')
                    field_type = resolved_annot.get('/FT')

                    if field_name and field_name in request.form:
                        if field_type == PyPDF2.generic.NameObject('/Btn'):  # Checkbox
                            value = '/Yes' if request.form[field_name] == 'Yes' else '/Off'
                            resolved_annot.update({
                                PyPDF2.generic.NameObject('/V'): PyPDF2.generic.NameObject(value),
                                PyPDF2.generic.NameObject('/AS'): PyPDF2.generic.NameObject(value)
                            })
                        else:  # Text field
                            resolved_annot.update({
                                PyPDF2.generic.NameObject('/V'): PyPDF2.generic.TextStringObject(request.form[field_name])
                            })

            writer.add_page(page)

        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return send_file(output_stream, as_attachment=True, download_name='modified_pdf.pdf')

    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)