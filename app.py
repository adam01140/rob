import logging
from flask import Flask, request, jsonify, send_from_directory, send_file, redirect, url_for, session
import PyPDF2
import io
import csv
import threading

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = 'your_secret_key_here'

# In-memory storage for users (not suitable for production)
users = {}



def save_data_to_csv():
    with open('user_data.csv', 'w', newline='') as csvfile:
        fieldnames = ['username', 'password', 'state', 'city']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for username, data in users.items():
            writer.writerow({'username': username, 'password': data['password'], 'state': data.get('state', ''), 'city': data.get('city', '')})

def load_data_from_csv():
    try:
        with open('user_data.csv', 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                users[row['username']] = {'password': row['password'], 'state': row['state'], 'city': row['city']}
    except FileNotFoundError:
        print("No existing CSV file found. Starting with an empty user database.")



def save_every_three_seconds():
    while True:
        save_data_to_csv()
        threading.Event().wait(3)




@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    if username in users:
        return 'Username already exists', 409
    users[username] = {'password': password, 'state': '', 'city': ''}  # Initialize with empty state and city
    return redirect(url_for('login'))
    
    
@app.route('/save_data', methods=['POST'])
def save_data():
    state = request.form['state']
    city = request.form['city']
    username = session.get('user')
    if not username:
        return jsonify({'error': 'User not logged in'}), 401
    if username in users:
        users[username].update({'state': state, 'city': city})
        save_data_to_csv()  # Save to CSV immediately after update
        print(f"Data saved for {username}: {users[username]}")
        return jsonify(success=True)
    else:
        return jsonify({'error': 'User does not exist'}), 404

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username]['password'] == password:
        session['user'] = username
        return redirect(url_for('index'))
    return 'Invalid credentials', 401



@app.route('/get_data', methods=['GET'])
def get_data():
    username = session.get('user')
    if not username:
        return jsonify({'error': 'User not logged in'}), 401
    user_data = users.get(username, {'state': '', 'city': ''})
    return jsonify(user_data)

   


def update_user_status(username, status):
    users = {}
    try:
        with open('user_data.csv', 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                users[row['username']] = row
            if username in users:
                users[username]['logged_status'] = status
    except FileNotFoundError:
        print("No existing CSV file found.")

    with open('user_data.csv', 'w', newline='') as csvfile:
        fieldnames = ['username', 'password', 'state', 'city', 'logged_status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for user in users.values():
            writer.writerow(user)


@app.route('/logout', methods=['POST'])
def logout():
    username = session.get('user')
    if username:
        update_user_status(username, 'yes')  # Function to update the CSV file
        session.pop('user', None)  # Log the user out by removing their session
        return jsonify({'success': 'Logged out successfully'}), 200
    return jsonify({'error': 'User not logged in'}), 401



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
    load_data_from_csv()  # Load data at start
    app.run(debug=True)



    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    