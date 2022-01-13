import os
import sqlite3
import requests
from flask import Flask, redirect, request, json, render_template, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps


def get_images(query, quantity):
    '''Fetches images form Pexels in category selected by users input || https://www.pexels.com/api/documentation/'''
    
    # Contact API
    try:
        api_key = "563492ad6f91700001000001eb0327b23e104114a74e566445718ba4"
        url = f"https://api.pexels.com/v1/search?query={query}&per_page={quantity}"
        response = requests.get(url, headers = { 'Authorization': api_key })
        response.raise_for_status()
        
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        images = []

        # Append URLs, picture and author and return a list of dicts (upending to the list of dictioniaries)
        for i in range(0, quantity):
            images.append({"image" : quote["photos"][i]["src"]["medium"],
                            "url" : quote["photos"][i]["url"],
                            "author" : quote["photos"][i]["photographer"]})
        return images
                
    except (KeyError, TypeError, ValueError):
        return None


def login_required(f):
    """Decorate routes to require login || https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def sorry(message, code=400):
    '''Returns apology message and error code'''

    return render_template("sorry.html", message=message, error_code=code), code


def get_username(database, table):
    '''Returns username, if he is logged in'''

    username = "Stranger"
    if session.get("user_id") is not None:
        # If we use Postgres
        if database == "postgres":
            app = Flask(__name__)   
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            db = SQLAlchemy(app)         
            user = db.session.query(table).filter(table.id == session["user_id"]).first()
            username = user.username          

        # If we use sqlite
        if database == "sqlite":
            memory = sqlite3.connect("memory.db")
            memory.row_factory = sqlite3.Row
            db = memory.cursor()
            rows = db.execute("SELECT username FROM users WHERE id = ?", [session["user_id"]])
                
            for row in rows:
                username = row["username"]
            memory.close()
            
    return username

