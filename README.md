# Memory - card game webapp
Simple web app - browser based game created with HTML, CSS, Python, Node.js and Sqlite. By using "Pexels" API it lets you play card game, where you look for matching pairs. Smooth look achieved with Bootstrap and Google fonts. 

#### Table of contents
* [Video Demo](#video-demo)
* [Description](#description)
* [Technologies](#technologies)
* [Features](#features)
* [Files](#files)
* [Setup](#setup)

#### Video Demo  <URL: HERE>

#### Description
This is a final project for Harvard's CS50 course. My goal was to use new learned technologies, memorize the material from course and have fun while doing it.
"Memory" is a web application - browser based game in which you can play a card game. The rules are simple: you are flipping the cards in search of matching pairs. The aim is to do it the fastest we can and with as little mistakes as possible. At the beginning of the game user can choose the amount of cards and type his own "game theme" in which cards-images will be displayed. To achieve customized game-theme app uses image stock API from Pexels. After the game we can check the images once more, see originals and authors name and add them to our favorites list, if we feel like it. In game we also keep score, taking into account how fast you were and how many consecutive match you got. Scores are displayed in separate tab, so we can compete between other users.

#### Technologies
Project is created with:
* Bootstrap 5.1
* Node.js 10.19.0
* Python 3.8.10
* Flask 2.0.2
* SQLite 3.31.1
* CSS
* HTML

Libraries:
* sqlite3
* flask
* flask_session
* requests

Projects uses image stock API:
* Pexels <URL: https://www.pexels.com/api/documentation/>

#### Features
* Register users
* Choose with how many cards you will play
* Choose your own game theme in which pictures from Pexels API will be displayed
* Save favourites images
* Delete images from favourites
* Record user score (if logged in)
* Record TOP 10 scores of the user
* Show TOP SCORES board of all users

#### Files

###### app.py
File containing all app functionalities from a back-end site. Written with Pythons Flask.
* Renders HTML templates
* Recives score after the game and saves it in the Sqlite databse
* Reads scores from database and renders in the HTML template
* Recives liked photo link and saves it in the database
* Deletes favourite pictures from database
* Register user
* Logs user in and out
* Renders yousers account template (his scores and favourite pictures)
* Specify users game (card amount and theme)
* Gets images from API and sends it to game template


###### helpers.py
Contains helping functions used in app.py. Contains function that:
* Fetches photos from Pexels API
* Decorate routes to require login, from: <URL: https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/>
* Returns apology and error code, if occured
* Returns username, if logged in

###### memory.db
Database in sqlite3.

###### /static
Folder containing static files:
* Images - backup images in case of API not responding
* Background image
* Icon
* Custom CSS

###### /templates
Folder containing HTML templates.
* game.html renders the actual card game and imgages that was used in it. Contains javascript functions that:
- recives data from Flask and translates it to javascript
- flips card and replece image with the one from Pexels API
- checks for match and records it
- keeps score
- counts bonus points
- renders after game screen
- shows cards used in game
- adds photos to favourites
* index.html renders homepage
* layout.html layout for other templates
* login.html log user in
* myaccount.html shows logged users his scores and images added to his favourites. With help of javascript user can delete photos.
* register.html register user
* scores.html shows table with best scores of all users
* sorry.html template used to show error message and code
* specify.html lets user specify the game 

#### Setup
To run this project, open its directory and run flask web server:
```
cd ../memory
python3 -m flask run
```