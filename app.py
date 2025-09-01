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

@app.route('/cities/<string:name>')
def loadCity(name):
    return f"Page to show weather of the city: {name}"


# API rotes below

@app.get('/api/cities')
def citiesListAPI():
    return [
        {"name": "New Delhi", "code": "new-delhi"},
        {"name": "Agra", "code": "agra"},
        {"name": "Lucknow", "code": "lucknow"},
    ]