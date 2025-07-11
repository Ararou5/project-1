from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import os # pour gerer les fichiers/dossiers
import json # pour lire et ecrire dans des fichiers json

app = Flask(__name__)                   # creation de Flask app
app.secret_key = 'votre_clef_secrete'  # pour securiser les sessions

DATA_FILE = os.path.join('data', 'users.json') #chemin vers le fichier ou sont stockes les utilisateurs
UPLOAD_FOLDER = os.path.join('uploads') #dossier ou seront enregistres les fichiers envoyes
os.makedirs(UPLOAD_FOLDER, exist_ok=True) #condition si le dossier n exist pas
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  #savoir ou chaque sera envoyes

@app.route('/register', methods=['GET', 'POST'])  #GET (affichage) et POST (soumission)
def register():
    if request.method == 'POST':#si l'utilisateur envoie le formulaire
        name = request.form['name'] 
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        new_user = {
            "name": name,
            "email": email,
            "password": password,
            "documents": []
        } #creation de l'utilisateur

        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'w') as f:
                json.dump([], f)  #si le fichier n'existe pas,on le cree (vide)

        with open(DATA_FILE, 'r+') as f:
            users = json.load(f)
            for u in users:
                if u['email'] == email:
                    return "Email déjà utilisé."
            users.append(new_user)
            f.seek(0)
            json.dump(users, f, indent=4) #verification de l'email et l'ajout de l'utilisateur

        return redirect('/login') #apres la fin d;inscription , retoure a la page de connexion
    return render_template('register.html') #si la methode est GET , on affich le formulaire d'inscription

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'] #recuperation des identifiants

        with open(DATA_FILE, 'r') as f:
            users = json.load(f)
            for user in users:
                if user['email'] == email and check_password_hash(user['password'], password):
                    session['user'] = user['email']
                    return redirect('/dashboard') # verification des infos , si corr , passer au dashboad
        return "Identifiants incorrects" #si non,err
    return render_template('login.html') #si GET, on affiche le formulaire


@app.route('/dashboard')
def dashboard(): #page principale apres connexion
    if 'user' not in session:
        return redirect('/login') #si l'utilisateur n'est pas connecte, retour a la page de connexion

    email = session['user']
    with open(DATA_FILE, 'r') as f:
        users = json.load(f)
        user_data = next((u for u in users if u['email'] == email), None) #recherche de l'utilisateur dans le fichier JSON

    return render_template('dashboard.html', user=user_data) #affichage du dashboard avec les infos de l'utilisateur

@app.route('/add-document', methods=['GET', 'POST'])
def add_document(): #page d'ajout des documents 
    if 'user' not in session:
        return redirect('/login') #si l'utilisateur n'est pas connecte, retour a la page de connexion

    if request.method == 'POST':
        title = request.form.get('title')
        file = request.files.get('file')#recuperation du titre et du fichier 

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
            json.dump(users, f, indent=4) #mis ajour des docs en fichier json
        return render_template('success.html', name=u["name"]) #page de succes
    return render_template('add_document.html') #si GET,on affiche le formulaire d'ajout


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename) #permition de telecharger un fichier depuis le dossier uploads

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login') #deconnexion , et retourne a la pas de login

if __name__ == '__main__':
    app.run(debug=True) #lancage en mode debug pour les errs
