from flask import Flask, render_template, request, redirect, session
from waitress import serve
from socket import gethostname, gethostbyname
from hashlib import sha256
from os import path, makedirs

from objects.sql import UserDatabase
from objects.directory_content import get_directory_content

app = Flask("Open Drive")
app.secret_key = "opendrive-zef15cezf1ce54fg1zc125dsq165fez1"

USER_DB = UserDatabase("./static/web/data/users.db")
DRIVE_PATH = "./static/drive/"

@app.route("/")
def index():
    if not 'username' in session:
        return redirect("/login")
    else:
        return redirect("/" + session['username'])

@app.route("/<username>")
def home(username: str) -> str:
    if not 'username' in session:
        return redirect("/login")
    
    if username != session['username']:
        return redirect(f"/{session['username']}")
    
    folders, files = get_directory_content(DRIVE_PATH + session['username'] + "/")
    return render_template("drive.html", folder=session['username'], files=files, folders=folders)

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
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form['username']
        password = sha256(request.form['password'].encode('utf-8')).hexdigest()
        
        # Check if username and password are correct
        if USER_DB.is_valid_user(username, password):
            session['username'] = USER_DB.get_user(username)[0]
            return redirect(f"/{session['username']}")
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
        makedirs(DRIVE_PATH + username)
        
        return redirect("/")

def main():
    app.run(host=gethostbyname(gethostname()), port=8080, debug=True) # Debug server
    # serve(app, host=gethostbyname(gethostname()), port=8080) # Production server

if __name__ == "__main__":
    main()
