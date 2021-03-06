import os
import sqlite3

from flask import Flask, request, render_template, session, redirect, jsonify, json
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from tempfile import mkdtemp
from string import punctuation
from random import shuffle, randint

from helpers import get_images, login_required, sorry, get_username


# Configure app
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/")
def index():
    '''Renders Homepage'''

    # Get username, if logged in
    username = get_username()

    return render_template("index.html", username=username)


@app.route("/getscores", methods=["POST"])
def getscores():
    '''Recives score after the game and saves it in the db'''

    # Data recived from javascript
    jsdata = request.form["js_data"]

    # Convert data from JSON dict to python dict
    data = json.loads(jsdata)

    score = data["score"]
    username = data["username"]

    # Open db and writes into it
    memory = sqlite3.connect("memory.db")
    db = memory.cursor()
    db.execute("""INSERT INTO scores (score, user_id, timestamp) VALUES (?, (SELECT id FROM users WHERE username = ?), 
               datetime(CURRENT_TIMESTAMP, 'localtime'));""", (score, username))

    # Save input and close it
    memory.commit()
    memory.close()
    
    # Return js data in order to avoid error ...
    return jsdata


@app.route("/deletephoto", methods=["POST"])
def deletephoto():
    '''Deletes pictures from db'''
    # Data from js
    js_data = request.form["js_data"]

    # Convert data to python dict
    data = json.loads(js_data)

    image = data["image"]
    username = data["username"]

    # Open db and execute queries
    memory = sqlite3.connect("memory.db")
    db = memory.cursor()

    # Check if photo is already in db
    rows = db.execute("""SELECT * FROM images WHERE user_id = (SELECT id FROM users WHERE username = ?) AND image = ?;""", (username, image))
   
    # Delete the photo
    db.execute("""DELETE FROM images WHERE user_id = (SELECT id FROM users WHERE username = ?) AND image = ?;""", (username, image))
    
    # Save input and close it
    memory.commit()
    memory.close()
    
    # Return js data in order to avoid error ...
    return jsdata


@app.route("/getlikes", methods=["POST"])
def getlikes():
    '''Recives liked photo link after the game and saves it in the db'''

    # Data recived from javascript
    jsdata = request.form["js_data"]

    # Convert data from JSON dict to python dict
    data = json.loads(jsdata)

    image = data["image"]
    url = data["url"]
    author = data["author"]
    username = data["username"]

    # Open db and writes into it
    memory = sqlite3.connect("memory.db")
    db = memory.cursor()

    # Check if photo is already in db
    rows = db.execute("""SELECT * FROM images WHERE user_id = (SELECT id FROM users WHERE username = ?) AND image = ?;""", (username, image))

    # Ensure username does not already exists ( fetchall() )
    if len(rows.fetchall()):
        memory.close()
        return jsdata

    db.execute("""INSERT INTO images (image, url, author, user_id) VALUES 
               (?, ?, ?, (SELECT id FROM users WHERE username = ?));""", (image, url, author, username))

    # Save input and close it
    memory.commit()
    memory.close()
    
    # Return js data in order to avoid error ...
    return jsdata


@app.route("/scores")
def scores():
    ''' Reads scores from database and renders it '''

    # Get username, if logged in
    username = get_username()
    
    # Initialize db
    memory = sqlite3.connect("memory.db")
    memory.row_factory = sqlite3.Row
    db = memory.cursor()
    
    # Query db
    top_scores = db.execute(""" SELECT users.username, scores.score FROM scores JOIN users
                            ON scores.user_id = users.id ORDER BY scores.score DESC LIMIT 10;""")
    # We dont close db (memory.clos()), becasue webpage cant operate on closed db 

    return render_template("scores.html", username=username, top_scores=top_scores)


@app.route("/login", methods=["GET", "POST"])
def login():
    ''' Log in the user'''
    
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Get users input
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Ensure proper input
        if not username:
            return sorry("Username is missing", 403)
        elif not password:
            return sorry("Password is missing", 403)

        # Initialize db, use row_factory to access data like in dict (still need to iterate over it)
        memory = sqlite3.connect("memory.db")
        memory.row_factory = sqlite3.Row
        db = memory.cursor()
         
        # Ensure username does not already exists ( fetchall(), instead of rows - db.execute, idk why it interfers with password check...)
        if len(db.execute("SELECT * FROM users WHERE username = ?", [username]).fetchall()) != 1:
            return sorry("Username does not exist", 403)

        # Check username in database (single input with [])
        rows = db.execute("SELECT * FROM users WHERE username = ?", [username])

        # Iterate over query (row_factory), get password and id
        hash_pass, userid = "",""
        for row in rows:
            hash_pass = row["hash"]
            userid = row["id"]
            
        # Compere password and hash
        if not check_password_hash(hash_pass, password):
            return sorry("Wrong password")
             
        # Remember the user
        session["user_id"] = userid
        
        return redirect("/")
        memory.close()
    
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    ''' Register the user'''

    if request.method == "POST":
        # Get users input
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure proper input
        if not username:
            return sorry("You should provide username", 403)
        elif not password or not confirmation:
            return sorry("You should provide password and confirm it", 403)
        elif len(password) < 5:
            return sorry("Password is too short", 403)
        elif password != confirmation:
            return sorry("Password and confirmation does not match", 403)
        
        # Ensure strong password (string fuction -> punctuation)
        special_char = punctuation
        special_char_check = False
        for word in password:
            if word in special_char:
                special_char_check = True
        if not special_char_check:
            return sorry("Password must contain at lest one special character", 403)      
        
        # Initialize db
        memory = sqlite3.connect("memory.db")
        db = memory.cursor()
         
        # Load username from database in rows (single input with [])
        rows = db.execute("SELECT * FROM users WHERE username = ?", [username])

        # Ensure username does not already exists ( fetchall() )
        if len(rows.fetchall()):
            return sorry("Username already taken")
        # Default color
        color = "default"

        # Hash password and insert user into db
        hash_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        db.execute("INSERT INTO users (username, hash, color) VALUES (?, ?, ?)", (username, hash_password, color))

        # Commit/save changes and redirect to users account
        memory.commit()
        memory.close()

        return redirect("/login")
        
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    '''Log user out'''

    # Forget any user_id
    session.clear()

    # Redirect user to homepage
    return redirect("/")


@app.route("/myaccount")
@login_required
def myaccount():
    '''Render yousers account (his scores and favourite pictures)'''

    # Get username, if logged in
    username = get_username()

    memory = sqlite3.connect("memory.db")
    memory.row_factory = sqlite3.Row
    db = memory.cursor()

    # Get scores from db
    your_score = db.execute(""" SELECT scores.score, scores.timestamp FROM scores JOIN users ON scores.user_id = users.id
                            WHERE users.username = ? ORDER BY scores.score DESC LIMIT 10;""", [username])
    
    scores = []
    for your in your_score:
        scores.append({"timestamp" : your["timestamp"], "score" : your["score"]})

    # Get photos info from db
    your_photos = db.execute(""" SELECT images.image, images.url, images.author FROM images JOIN users ON images.user_id = users.id
                            WHERE users.username = ?;""", [username])
    
    photos = []
    for photo in your_photos:
        photos.append({"image" : photo["image"], "url" : photo["url"], "author" : photo["author"]})
        
    memory.close()
      
    # We dont close db (memory.close()), becasue webpage cant operate on closed db 

    return render_template("myaccount.html", username=username, your_score=scores, your_photos=photos)


@app.route("/specify")
def specify():
    '''Renders specify'''

    # Get username, if logged in
    username = get_username()

    return render_template("specify.html", username=username)


@app.route("/game", methods=["GET", "POST"])
def game():
    '''Creates game that user defined, gets photos form API'''

    # Get username, if logged in
    username = get_username()

    if request.method == "POST":
        # Get users input
        try:
            cards_quantity = int(request.form.get("cards_quantity"))
        except:
            return sorry("You did not provide number of cards. Choose from dropdown list")
        game_theme = request.form.get("game_theme").strip().replace(" ", "+")

        # Check users input
        if not cards_quantity or not game_theme:
            return sorry("You did not provide theme or number of cards. Mayby next time try a Quick Start!")
        if cards_quantity not in [12, 24, 36]:
            return sorry("Looks like you choose wrong card number")
        
        # Calculate pairs
        pairs = int(cards_quantity / 2)

        # Quick game case
        if game_theme == "no_users_input":
            game_themes = ["moutains", "flowers", "animals", "country", "christmas", "ladnscape", "london", "new york", "garden", "trees", "space", "sky", "clouds", "random", "paris", "dolomites"]
            index = randint(0, len(game_themes) - 1)
            game_theme = game_themes[index]
                
        try:
            # Pass users input into API-function
            images = get_images(game_theme, pairs)

            # Make list twice as big and shuffle it for random placement
            images = images + images
            shuffle(images)

        except:
            # In case API does not respond - append static images
            images = []           
            for i in range(0, pairs):
                images.append({"image" : f"../static/images/{i}.jpeg"})

            # Make list twice as big and shuffle it for random placement
            images = images + images
            shuffle(images)

        return render_template("game.html", pairs=pairs, memory=images, username=username, game_theme=game_theme)

    else:
        return redirect("/specify")