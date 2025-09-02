from flask import Flask, url_for

app = Flask(__name__)

cities = [
    {"id": 1, "name": "New Delhi", "code": "new-delhi", "country": "India"},
    {"id": 2, "name": "Agra", "code": "agra", "country": "India"},
    {"id": 3, "name": "Lucknow", "code": "lucknow", "country": "India"},
    {"id": 4, "name": "Mumbai", "code": "mumbai", "country": "India"},
]

@app.route('/')
def homePage():
    return "Page to show weather of my current city & list down table of all the cities loaded from database"


@app.route('/cities')
def citiesListPage():
    return "Page to show list of cities"


@app.route('/cities/add')
def addCityPage():
    return "Page to show a form to add a city in the database"

@app.route('/cities/<int:id>')
def loadCity(id):
    return f"Page to show weather of the city: {cities[id]['name']}"

@app.get("/api/get-all-links")
def getAllLinksAPI():
    return {
        "status": "success",
        "message": "All API links loaded successfully",
        "data": {
            "pages": {
                "home": url_for('homePage'),
                "citiesList": url_for('citiesListPage'),
                'addCity': url_for('addCityPage'),
                'loadCity': url_for('loadCity', id = 3),
            },
            "api": {
                "listCities": url_for('citiesListAPI'),
                "addCity": url_for('addCityAPI'),
                "deleteCity": url_for('deleteCityAPI', id=2),
                "loadWeatherAllCities": url_for('loadWeatherAPI'),
                "loadWeatherOfACity": url_for('loadWeatherOfACity', cityId=1),
            }
        }
    }


## API rotes below

# API to list all cities
@app.get('/api/cities')
def citiesListAPI():
    return {
        "status": "success",
        "message": "Cities loaded successfully",
        "data": {
            "cities": cities
        }
    }

# API to create a new city
@app.post('/api/cities')
def addCityAPI():
    return {
        "status": "success",
        "message": "City added successfully",
        "city": cities[2]
    }

# API to delete a city
@app.delete("/api/cities/<int:id>")
def deleteCityAPI(id):
    return {
        "status": "success",
        "message": f"City with ID {id} (Name: {cities[id]['name']}) has been deleted"
    }

# API to load weather of all the cities
@app.get("/api/weather")
def loadWeatherAPI():
    weather = []
    for city in cities:
        weather.append({
            "id": city['id'],
            "name": city['name'],
            "code": city['code'],
            "country": city['country'],
            "weather": {
                "temperature": "30 °C",
                "condition": "Sunny",
                "humidity": "60%",
                "wind": "10 km/h"
            }
        })

    return {
        "status": "success",
        "message": "Weather for all the cities loaded successfully",
        "data": {
            "weather": weather
        }
    }

# Get weather of a particular city
@app.get("/api/weather/<int:cityId>")
def loadWeatherOfACity(cityId):
    return {
        "status": "success",
        "message": f"Weather for city ID {cityId} (Name: {cities[cityId]['name']}) loaded successfully",
        "data": {
            "weather": {
                "temperature": "30 °C",
                "condition": "Sunny",
                "humidity": "60%",
                "wind": "10 km/h"
            }
        }
    }