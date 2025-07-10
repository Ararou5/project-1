from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

app = Flask(__name__)
app.secret_key = 'votre_clef_secrete'  # Change cette clé pour ton projet

# Chemins
DATA_FILE = os.path.join('data', 'users.json')
UPLOAD_FOLDER = os.path.join('uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # ✅ Ajout indispensable

# PAGE : Inscription
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        new_user = {
            "name": name,
            "email": email,
            "password": password,
            "documents": []
        }

        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'w') as f:
                json.dump([], f)

        with open(DATA_FILE, 'r+') as f:
            users = json.load(f)
            for u in users:
                if u['email'] == email:
                    return "Email déjà utilisé."
            users.append(new_user)
            f.seek(0)
            json.dump(users, f, indent=4)

        return redirect('/login')
    return render_template('register.html')

# PAGE : Connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with open(DATA_FILE, 'r') as f:
            users = json.load(f)
            for user in users:
                if user['email'] == email and check_password_hash(user['password'], password):
                    session['user'] = user['email']
                    return redirect('/dashboard')
        return "Identifiants incorrects"
    return render_template('login.html')

# PAGE : Tableau de bord
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    email = session['user']
    with open(DATA_FILE, 'r') as f:
        users = json.load(f)
        user_data = next((u for u in users if u['email'] == email), None)

    return render_template('dashboard.html', user=user_data)

# PAGE : Ajout de document
@app.route('/add-document', methods=['GET', 'POST'])
def add_document():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form.get('title')
        file = request.files.get('file')

        with open(DATA_FILE, 'r+') as f:
            users = json.load(f)
            for u in users:
                if u['email'] == session['user']:
                    if title:
                        u['documents'].append({"type": "text", "title": title})
                    if file and file.filename != "":
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                        file.save(filepath)
                        u['documents'].append({"type": "file", "filename": file.filename})
                    break
            f.seek(0)
            json.dump(users, f, indent=4)
        return render_template('success.html', name=u["name"])
    return render_template('add_document.html')

# Télécharger un fichier
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Déconnexion
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
