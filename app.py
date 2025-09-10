from flask import Flask, url_for, render_template, request, abort
import os
import requests

app = Flask(__name__)

cities = [
    {"id": 1, "name": "New Delhi", "code": "new-delhi", "country": "India"},
    {"id": 2, "name": "Agra", "code": "agra", "country": "India"},
    {"id": 3, "name": "Lucknow", "code": "lucknow", "country": "India"},
    {"id": 4, "name": "Mumbai", "code": "mumbai", "country": "India"},
]

@app.route('/')
def homePage():
    return render_template('pages/home.html')


@app.route('/cities')
def citiesListPage():
    return render_template('pages/cities/list.html', cities = cities)


@app.route('/cities/add')
def addCityPage():
    return "Page to show a form to add a city in the database"


@app.route('/cities/<int:id>')
def loadCity(id):
    city = getCityById(id)

    if city is None:
        abort(404, description='city_not_found')

    cityWeather = loadWeatherOfACity(id)['data']['weather']
    return render_template('pages/cities/view.html', city = city, weather = cityWeather)


@app.get("/api/utils/get-all-links")
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


@app.route('/api/utils/dump-request-attributes', methods=['GET', 'POST'])
def dumpAllRequestAttributes():
    return {
        "status": "success",
        "message": "Request attributes dumped successfully",
        "data": {
            "args": request.args,
            "form": request.form,
            "values": request.values,
            # "json": request.json,
            # "files": request.files,
            "headers": dict(request.headers),
            "cookies": request.cookies,
            "method": request.method,
            "url": request.url,
            "base_url": request.base_url,
            "url_root": request.url_root,
            "path": request.path,
            "full_path": request.full_path,
            "script_root": request.script_root,
            "remote_addr": request.remote_addr,
            "user_agent": str(request.user_agent),
        }
    }


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
    city = getCityById(cityId)

    queryParams = {
        'appid': os.getenv('WEATHER_API_KEY'),
        'units': 'metric',
        'q': city['name']
    }
    weatherResponse = requests.get("https://api.openweathermap.org/data/2.5/weather", params=queryParams)
    apiResponse = weatherResponse.json()

    return {
        "status": "success",
        "message": f"Weather for city ID {cityId} (Name: {city['name']}) loaded successfully",
        "data": {
            "weather": {
                "temperature": f"{apiResponse['main']['temp']}°C",
                "condition": apiResponse['weather'][0]['description'],
                "humidity": f"{apiResponse['main']['humidity']}%",
                "wind": f"{apiResponse['wind']['speed']} km/h",
                "feelsLike": f"{apiResponse['main']['feels_like']}°C",
            }
        }
    }


def getCityIndexById(id):
    index = None

    for i, city in enumerate(cities):
        if city['id'] == id:
            index = i

    return index


def getCityById(id):
    index = getCityIndexById(id)

    if index is not None:
        return cities[index]
    else:
        return None


@app.errorhandler(404)
def errorHandler404(error):
    match error.description:
        case 'city_not_found':
            return render_template('pages/cities/notFound.html'), 404
        case _:
            return render_template('pages/errors/404.html'), 404