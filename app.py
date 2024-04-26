
    
    
    
    
    
    
    
    
    
from flask import Flask, request, jsonify, send_from_directory, send_file, redirect, url_for, session
import PyPDF2
import io

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = 'your_secret_key_here'

# In-memory storage for users (not suitable for production)
users = {}

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    if username in users:
        return 'Username already exists', 409
    users[username] = password
    return redirect(url_for('login'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username] == password:
        session['user'] = username
        return redirect(url_for('index'))
    return 'Invalid credentials', 401

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route('/check_login')
def check_login():
    if 'user' in session:
        return jsonify({'status': 'logged in'}), 200
    return jsonify({'status': 'not logged in'}), 401



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

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
from flask import Flask, request, jsonify, send_from_directory, send_file, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import PyPDF2
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your-secret-key'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('login'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        return redirect(url_for('index'))
    return 'Login Failed'

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Your existing routes below
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
