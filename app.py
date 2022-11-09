from cs50 import SQL
from flask import Flask, render_template, request, redirect, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required



app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///froshims.db")

"""
.schema | CREATE TABLE registrants (id INTEGER, username TEXT NOT NULL, hash TEXT NOT NULL, PRIMARY KEY(id));
* | SELECT * FROM registrants;

"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Forget any user id
    # session.clear()

    if request.method == 'POST':

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)
        
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["userID"]

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect('/')

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 403)
        
        # Ensure password matches confirmation
        elif not confirmation:
            return apology("must confirm password", 403)
        
        # Query database for username, should only yield one row
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure that username does not match another
        if rows:
            return apology("username already exists", 403)
        
        # Ensure that password equals confirmation
        if password != confirmation:
            return apology("passwords do not match", 403)

        password_hash = generate_password_hash(password)

        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, password_hash)
        return render_template("login.html")
    else:
        print("GET")
        return render_template("register.html")

@app.route("/")
@login_required
def index():
    user = db.execute("SELECT * FROM users WHERE userID = ?", session["user_id"])
    return render_template("index.html", user=user[0]["username"])

@app.route("/group")
@login_required
def group():
    user = db.execute("SELECT * FROM users WHERE userID = ?", session["user_id"])
    group_id = user[0]["userGroup"]
    if not group_id:
        return apology("You are not in a group", 403)
    
    data = db.execute("SELECT groupName FROM groups WHERE groupID = ?", group_id)
    group_name = data[0]["groupName"]
    members = db.execute("SELECT * FROM users WHERE userGroup = ? AND userID != ?", group_id, session["user_id"])
    return render_template("group.html", group_name=group_name, members=members)

@app.route("/join", methods=["GET", "POST"])
@login_required
def join():
    if request.method == "POST":
        group = request.form.get("groupname")

        # Ensure group name was submitted
        if not group:
            return apology("must provide group name", 403)
        
        # Get groupID
        data = db.execute("SELECT groupID FROM groups WHERE groupName = ?", group)

        # Ensure group exists
        if not data:
            return apology("group does not exist", 403)
        
        groupID = data[0]["groupID"]
        # Add user to group
        db.execute("UPDATE users SET userGroup = ? WHERE userID = ?", groupID, session["user_id"])

        return redirect("/group")
    else:
        return render_template("join.html")

@app.route("/leave", methods=["POST"])
@login_required
def leave():
    db.execute("UPDATE users SET userGroup = NULL WHERE userID = ?", session["user_id"])
    return redirect("/group")

@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        group = request.form.get("groupname")

        # Ensure group name was submitted
        if not group:
            return apology("must provide group name", 403)
        
        # Query database for group name, should only yield one row
        rows = db.execute("SELECT * FROM groups WHERE groupName = ?", group)

        # Ensure that group name does not match another
        if rows:
            return apology("group name already exists", 403)
        
        # Add group to groups table
        db.execute("INSERT INTO groups (groupName) VALUES (?)", group)

        # Get groupID
        data = db.execute("SELECT groupID FROM groups WHERE groupName = ?", group)
        groupID = data[0]["groupID"]

        # Add user to group
        db.execute("UPDATE users SET userGroup = ? WHERE userID = ?", groupID, session["user_id"])

        return redirect("/group")
    else:
        return render_template("create.html")

@app.route("/profile")
@login_required
def profile():
    user = db.execute("SELECT * FROM users WHERE userID = ?", session["user_id"])
    username = user[0]["username"]
    groupID = user[0]["userGroup"]
    if not groupID:
        return render_template("profile.html", username=username, group="None")
    data = db.execute("SELECT groupName FROM groups WHERE groupID = ?", groupID)
    group = data[0]["groupName"]
    return render_template("profile.html", username=username, group=group)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


"""
@app.route('/deregister', methods=['POST'])
def deregister():

    # Forget the user
    id = request.form.get('id')
    if id:
        db.execute('DELETE FROM registrants WHERE id = ?', id)
    return redirect('/registrants')

@app.route('/registrants')
def registrants():
    registrants=db.execute('SELECT * FROM registrants')
    return render_template('registrants.html', registrants=registrants)
"""


