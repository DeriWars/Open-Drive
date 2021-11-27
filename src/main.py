from flask import Flask, render_template, request, redirect, session
from waitress import serve
from socket import gethostname, gethostbyname
from hashlib import sha256
from os import path, makedirs, remove
from shutil import rmtree

from objects.sql import UserDatabase, FolderDatabase
from objects.directory_content import get_directory_content

app = Flask("Pécloud")
app.secret_key = "opendrive-zef15cezf1ce54fg1zc125dsq165fez1"

app.config['UPLOAD_FOLDER'] = "./static/upload"

USER_DB = UserDatabase("./static/web/data/users.db")
FOLDER_DB = FolderDatabase("./static/web/data/folder.db")
DRIVE_PATH = "./static/drive/"

def get_real_content(path: str, username: str):
    folders, files = get_directory_content(path)
    
    if folders != None or len(folders) > 0:
        for i in range(len(folders)):
            folders[i] = [folders[i], FOLDER_DB.get_folder_by_id(folders[i], username)[0]]
    
    return folders, files

@app.route("/")
def index():
    if not 'username' in session:
        return redirect("/login")
    else:
        return redirect("/" + session['username'] + "/root")

@app.route("/<username>/<folder_id>")
def folder(username: str, folder_id: str) -> str:
    if not 'username' in session:
        return redirect("/login")
    
    if username != session['username']:
        return redirect(f"/{session['username']}")
    print(session['path'])
    if folder_id != "root":
        folder = FOLDER_DB.get_folder_by_id(folder_id, session['username'])
        
        if folder is None:
            return redirect(f"/{session['username']}/root")
        
        folders, files = get_real_content(folder[3], session['username'])
        
        session['path'] = folder[3]
        session['web_path'] = f"/{username}/{folder_id}"
        
        return render_template("drive.html", username=username, folder=session['path'][1:], files=files, folders=folders, current_folder=folder[1], folder_name=folder[0])
    else:
        folder = FOLDER_DB.get_folder_by_name(session['username'], session['username'])
        
        if folder is None:
            return redirect(f"/{session['username']}/root")
        
        folders, files = get_real_content(folder[3], session['username'])
        
        session['path'] = folder[3]
        session['web_path'] = f"/{username}/{folder_id}"
        
        return render_template("drive.html", username=username, folder=session['path'][1:], files=files, folders=folders, current_folder=folder[1], folder_name="Your folders")

@app.route("/shared")
def shared() -> str:
    if not 'username' in session:
        return redirect("/login")
    
    return render_template("drive.html", folder=session['username'], files=[], folders=[])

@app.route("/login", methods=["GET", "POST"])
def login() -> str:
    """
    Login page

    Returns:
        str: login page or drive page if logged in
    """
    
    if request.method == "GET":
        session.pop('username', None)
        session.pop('path', None)
        session.pop('web_path', None)
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form['username']
        password = sha256(request.form['password'].encode('utf-8')).hexdigest()
        
        # Check if username and password are correct
        if USER_DB.is_valid_user(username, password):
            session['username'] = USER_DB.get_user(username)[0]
            return redirect("/")
        else:
            return render_template("login.html", error="Username and password given does not match any user.")

@app.route("/signup", methods=["GET", "POST"])
def signup() -> str:
    """
    Signup page
    
    Returns:
        str: the web page to render
    """
    if request.method == "GET":
        session.pop('username', None)
        return render_template("signup.html")
    elif request.method == "POST":
        username = request.form['username']
        password = sha256(request.form['password'].encode('utf-8')).hexdigest()
        email = request.form['email']
        confirm_password = sha256(request.form['confirm_password'].encode('utf-8')).hexdigest()

        # Check if username is already taken
        if USER_DB.get_user(username, email) is not None:
            return render_template("signup.html", error="This username is already taken!")
        
        # Check if passwords match
        if password != confirm_password:
            return render_template("signup.html", error="Passwords does not match.")
        
        # Add user to database
        USER_DB.add_user(username, email, password)
        identity = FOLDER_DB.add_folder(username, username, DRIVE_PATH)
        makedirs(DRIVE_PATH + identity)
        
        return redirect("/")

@app.route("/upload", methods=["POST"])
def upload() -> str:
    if not 'username' in session:
        return redirect("/login")
    
    if request.method == "POST":
        if 'file' in request.files:
            for file in request.files.getlist('file'):
                file.save(f"{session['path']}{file.filename}")
                
            return redirect(f"{session['web_path']}")
            
    return redirect(f"{session['web_path']}")

@app.route("/new", methods=["POST"])
def new_folder():
    if not 'username' in session:
        return redirect("/login")
    
    if request.method == "POST":
        folder_name = request.form['folder_name']
        identity = FOLDER_DB.add_folder(folder_name, session['username'], session['path'])
        folder = FOLDER_DB.get_folder_by_name(session['username'], session['username'])
        makedirs(f"{session['path']}{identity}")
    
    return redirect(f"{session['web_path']}")

@app.route("/delete/<folder_id>/<file>")
def delete_file(folder_id: str, file: str) -> str:
    if not 'username' in session:
        return redirect("/login")
    
    folder = FOLDER_DB.get_folder_by_id(folder_id, session['username'])
    
    if path.exists(f"{folder[3]}{file}"):
        remove(f"{folder[3]}{file}")
    
    return redirect(f"{session['web_path']}")

@app.route("/delete/<folder_id>")
def delete_folder(folder_id: str) -> str:
    if not 'username' in session:
        return redirect("/login")
    
    folder = FOLDER_DB.get_folder_by_id(folder_id, session['username'])
    
    if path.exists(f"{folder[3]}") and folder != None:
        FOLDER_DB.delete_folder(folder_id)
        rmtree(f"{folder[3]}",)
    
    return redirect(f"{session['web_path']}")

def main():
    app.run(host=gethostbyname(gethostname()), port=8080, debug=True) # Debug server
    # serve(app, host=gethostbyname(gethostname()), port=8080) # Production server

if __name__ == "__main__":
    main()
