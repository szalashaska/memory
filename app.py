import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, render_template, session, redirect, json
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from tempfile import mkdtemp
from string import punctuation
from random import shuffle, randint
from datetime import datetime

from helpers import get_images, login_required, sorry, get_username

# Environment settings
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Choose between Postgres and Sqlite: "postgres" or "sqlite" 
DB_TYPE = "postgres"

# Choose between development and production: "dev" or "prod"
ENV = "prod"

# Import Datbase modul
if DB_TYPE == "postgres":
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy.pool import NullPool
    print("postgres")

else:
    import sqlite3
    # If we use Sqlite we do not need declare Username variable to avoid error
    Users = ""
    print("sqlite")


# Configure app
app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

''' When using Postgres DB '''
if DB_TYPE == "postgres":
    if ENV == "dev":
        # ...//username:password@localhost/database_name
        app.config['SQLALCHEMY_DATABASE_URI'] = ''
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = { 'poolclass': NullPool, }

    else:
        app.debug = False
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = { 'poolclass': NullPool, }
    # Switching of modification tracking and setting up the DB
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = SQLAlchemy(app)
    
    # Creating DB model: table users, scores and images
    class Users(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(50), unique=True)
        hash = db.Column(db.String(200))
        scores = db.relationship('Scores', backref='users')
        images = db.relationship('Images', backref='users')

        def __init__(self, username, hash):
            self.username = username
            self.hash = hash

    class Scores(db.Model):
        __tablename__ = 'scores'
        scores_id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
        score = db.Column(db.Integer)
        timestamp = db.Column(db.DateTime, default=datetime.now().strftime("%x %X"), nullable=False)

        def __init__(self, user_id, score):
            self.user_id = user_id
            self.score = score

    class Images(db.Model):
        __tablename__ = 'images'
        images_id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
        image = db.Column(db.String(200), nullable=False)
        url = db.Column(db.String(200), nullable=False)
        author = db.Column(db.String(200))

        def __init__(self, user_id, image, url, author):
            self.user_id = user_id
            self.image = image
            self.url = url
            self.author = author
            ''' End of Postgres configuration '''


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
    jsdata = request.get_json()
    score = jsdata["score"]
    username = jsdata["username"]

    # If we use Postgres
    if DB_TYPE == "postgres":
        # Initialize db
        db = SQLAlchemy(app)

        # Get user id
        user = db.session.query(Users).filter(Users.username == username).first()
        
        # Prepare data
        data = Scores(user.id, score)

        # Add and commit data to db
        db.session.add(data)
        db.session.commit()
        db.session.close()
        
        return jsdata

    # If we use Sqlite
    else:
        # Open db and writes into it
        memory = sqlite3.connect("memory.db")
        db = memory.cursor()
        db.execute("""INSERT INTO scores (score, user_id, timestamp) VALUES (?, (SELECT id FROM users WHERE username = ?), 
                datetime(CURRENT_TIMESTAMP, 'localtime'));""", (score, username))

        # Save input and close it
        memory.commit()
        memory.close()
        
        return jsdata


@app.route("/deletephoto", methods=["POST"])
def deletephoto():
    '''Deletes pictures from db'''
    # Data from js
    jsdata = request.get_json()
    image = jsdata["image"]
    username = jsdata["username"]

    # If we use Postgres
    if DB_TYPE == "postgres":
        db = SQLAlchemy(app)

        user = db.session.query(Users).filter(Users.username == username).first()
        photo = db.session.query(Images).filter(Images.image == image, Images.user_id == user.id).first()
        
        # Check if image exists and delete if so
        if photo:
            db.session.delete(photo)
            db.session.commit()
            db.session.close()

    # If we use Sqlite
    else:
        # Open db and execute queries
        memory = sqlite3.connect("memory.db")
        db = memory.cursor()

        # Check if photo is already db
        rows = db.execute("""SELECT * FROM images WHERE user_id = (SELECT id FROM users WHERE username = ?) AND image = ?;""", (username, image))
        if len(rows.fetchall()) == 0:
            return jsdata
    
        # Delete the photo
        db.execute("""DELETE FROM images WHERE user_id = (SELECT id FROM users WHERE username = ?) AND image = ?;""", (username, image))
        
        # Save input and close it
        memory.commit()
        memory.close()
    
    return jsdata


@app.route("/getlikes", methods=["POST"])
def getlikes():
    '''Recives liked photo link after the game and saves it in the db'''
    # Data recived from javascript
    jsdata = request.get_json()
    image = jsdata["image"]
    url = jsdata["url"]
    author = jsdata["author"]
    username = jsdata["username"]

    # If we use "postgres"
    if DB_TYPE == "postgres":
        db = SQLAlchemy(app)

        # If image alredy exists
        if db.session.query(Images).filter(Images.image == image).count() == 1:
            return jsdata

        # Get user id
        user = db.session.query(Users).filter(Users.username == username).first()

        # Insert into database
        data = Images(user.id, image, url, author)
        db.session.add(data)
        db.session.commit()
        db.session.close()

    # If we use "sqlite"
    else:
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
    
    # If we use Postgres
    if DB_TYPE == "postgres":
        db = SQLAlchemy(app)
        # with_entities creates one object, instead of to objects as default
        # order of command may matter
        top_scores = db.session.query(Scores, Users).join(Users).with_entities(Scores.score, Users.username).order_by(Scores.score.desc()).limit(10).all()
        db.session.close()
        
    # If we use Sqlite
    else:
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

        # If we use Postgres    
        if DB_TYPE == "postgres":

            # Initialize db
            db = SQLAlchemy(app)

            # Check if user exists
            if db.session.query(Users).filter(Users.username == username).count() != 1:
                return sorry("Username does not exist", 403)

            # Query for user in db, get id and password hash
            user = db.session.query(Users).filter(Users.username == username).first()
            
            hash_pass = user.hash
            userid = user.id

            # Check if password is correct
            if not check_password_hash(hash_pass, password):
                return sorry("Wrong password")

            # Remember the user
            session["user_id"] = userid
            session["user"] = username

            db.session.close()
            
            return redirect("/")

        # If we use Sqlite
        else:
            # Initialize db, use row_factory to access data like in dict (still need to iterate over it)
            memory = sqlite3.connect("memory.db")
            memory.row_factory = sqlite3.Row
            db = memory.cursor()
            
            # Ensure username exists ( fetchall(), instead of rows - db.execute, idk why it interfers with password check...)
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

        # If we use Postgres    
        if DB_TYPE == "postgres":
            db = SQLAlchemy(app)
            # Ensure username does not already exists
            if db.session.query(Users).filter(Users.username == username).count() == 0:
                # Hash password and insert user into db
                hash_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

                data = Users(username, hash_password)
                db.session.add(data)

                # Commit/save changes and redirect to users account
                db.session.commit()
                db.session.close()

                return redirect("/login")
            else:
                # Return apology if username was alredy taken
                return sorry("Username already taken")     
        
        # If we use Sqlite
        else:
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
    '''Render users account (his scores and favourite pictures)'''

    # Get username, if logged in
    username = get_username()

    #If we use Postgres
    if DB_TYPE == "postgres":
        db = SQLAlchemy(app)

        # Get scores 
        scores = db.session.query(Scores, Users).join(Users).where(Users.username == username).with_entities(Scores.score, Scores.timestamp).order_by(Scores.score.desc()).limit(10).all()

        # Get images
        photos = db.session.query(Images, Users).join(Users).where(Users.username == username).with_entities(Images.image, Images.url, Images.author).all()

        db.session.close()

    # If we use Sqlite
    else:
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
        request_card_number = request.form.get("cards_quantity") 
      
        cards_quantity = int(request_card_number) if request_card_number else 12 
       
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
            game_themes = ["moutains", "flowers", "animals", "country", "christmas", "ladnscape", "london", "new york",
                          "garden", "trees", "space", "sky", "clouds", "random", "paris", "dolomites"]
            index = randint(0, len(game_themes) - 1)
            game_theme = game_themes[index]
                
        try:
            # Pass users input into API-function
            images = get_images(game_theme, pairs)         

        except:
            # In case API does not respond - append static images
            images = []           
            for i in range(0, pairs):
                images.append({"image" : f"../static/images/{i}.jpeg"})

        # Make list twice as big and shuffle it for random placement
        game = images + images
        shuffle(game)

        return render_template("game.html", pairs=pairs, images=images, memory=game, username=username, game_theme=game_theme)

    else:
        return redirect("/specify")

if __name__ == '__main__':
    app.run()
