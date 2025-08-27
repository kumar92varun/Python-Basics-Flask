from flask import Flask

app = Flask(__name__)

@app.route('/')
def homePage():
    return "Page to show weather of my current city & list down table of all the cities loaded from database"


@app.route('/cities')
def citiesListPage():
    return "Page to show list of cities"


@app.route('/cities/add')
def addCityPage():
    return "Page to show a form to add a city in the database"