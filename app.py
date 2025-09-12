from flask import Flask, url_for, render_template, request, abort
import os
import requests

app = Flask(__name__)

blogData = {
    "clientName": "First Name",
    "clientEmail": "email@address.com",
    "utmCampaign": "2025-sept",
    "utmSource": "cs",
    "utmMedium": "tech-mail",
    "utmContent": "cs-vk",

    "mailSubject": "Thought you might find this interesting - from Crownstack",
    "blogUrl": "https://blog.crownstack.com/blog/qa/sdks-explained-for-qas",
    "blogTitle": "SDKs explained for QAs: what they are, what to test, and how",
    "blogDescription": "From a QA perspective, this blog explains what an SDK is, breaks down its various components, highlights how it differs from an API, and provides practical guidance on what and how to test - including negative testing approaches.",
}
blogData['blogUrl'] = f"{blogData['blogUrl']}?utm_campaign={blogData['utmCampaign']}&utm_source={blogData['utmSource']}&utm_medium={blogData['utmMedium']}&utm_content={blogData['utmContent']}"


@app.route('/')
def homePage():
    return render_template('pages/home.html')


@app.route('/cities')
def citiesListPage():
    cities = getCitiesList()
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


@app.get('/mailers/view')
def viewMailer():
    return render_template('mailers/view.html', 
        clientName=blogData['clientName'], 
        blogUrl=blogData['blogUrl'], 
        blogTitle=blogData['blogTitle'], 
        blogDescription=blogData['blogDescription']
    )

@app.get('/mailers/send')
def sendMailer():
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.utils import formataddr

    # Gmail credentials
    EMAIL = os.getenv('MAIL_SENDER_EMAIL')
    PASSWORD = os.getenv('MAIL_SENDER_PASSWORD')  # Use App Password, not your Gmail login password

    # Email details
    TO_EMAIL = blogData['clientEmail']
    SUBJECT = blogData['mailSubject']

    # HTML content
    HTML_CONTENT = render_template('mailers/view.html', 
        clientName=blogData['clientName'], 
        blogUrl=blogData['blogUrl'], 
        blogTitle=blogData['blogTitle'], 
        blogDescription=blogData['blogDescription']
    )

    # Create message container
    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((os.getenv('MAIL_SENDER_NAME'), os.getenv('MAIL_SENDER_EMAIL')))
    msg["To"] = TO_EMAIL
    msg["Subject"] = SUBJECT

    # Attach the HTML body
    msg.attach(MIMEText(HTML_CONTENT, "html"))

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)

        # Send email
        server.sendmail(EMAIL, TO_EMAIL, msg.as_string())
        return "✅ HTML email sent successfully!"

        server.quit()
    except Exception as e:
        return "❌ Error:"




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
    cities = getCitiesList()
    cities = [dict(row._mapping) for row in cities]

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
    from flask import request
    from sqlalchemy import create_engine, text
    engine = create_engine("mysql+pymysql://root:toor@localhost:3306/others_flask_demo")
    connection = engine.connect()
    result = connection.execute(text(f"INSERT INTO cities (name, code) VALUES ('{request.form['name']}', '{request.form['code']}')"))
    connection.commit()

    return {
        "status": "success",
        "message": "City added successfully",
        "cityId": result.lastrowid
    }


# API to delete a city
@app.delete("/api/cities/<int:id>")
def deleteCityAPI(id):
    return {
        "status": "success",
        "message": f"City with ID {id} (Name: {cities[id]['name']}) has been deleted"
    }


# Get weather of a particular city
@app.get("/api/weather/<int:cityId>")
def loadWeatherOfACity(cityId):
    city = getCityById(cityId)
    if city is None:
        return {
            "status": "error",
            "message": f"City with ID {cityId} not found in the database",
            "data": {}
        }

    queryParams = {
        'appid': os.getenv('WEATHER_API_KEY'),
        'units': 'metric',
        'q': city['name']
    }
    weatherResponse = requests.get("https://api.openweathermap.org/data/2.5/weather", params=queryParams)
    apiResponse = weatherResponse.json()

    if apiResponse['cod'] != 200:
        return {
            "status": "error",
            "message": f"Weather for city ID {cityId} could not be loaded. API response: {apiResponse['message']}",
            "data": {}
        }

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

def getCitiesList():
    from sqlalchemy import create_engine, text

    engine = create_engine("mysql+pymysql://root:toor@localhost:3306/others_flask_demo")
    connection = engine.connect()
    result = connection.execute(text("SELECT id,name,code FROM cities"))
    cities = result.fetchall()
    return cities


def getCityById(id):
    from sqlalchemy import create_engine, text

    engine = create_engine("mysql+pymysql://root:toor@localhost:3306/others_flask_demo")
    connection = engine.connect()
    result = connection.execute(text(f"SELECT id,name,code FROM cities WHERE id = {id}"))
    city = result.fetchone()
    if city is None:
        return None
    return dict(city._mapping)


@app.errorhandler(404)
def errorHandler404(error):
    match error.description:
        case 'city_not_found':
            return render_template('pages/cities/notFound.html'), 404
        case _:
            return render_template('pages/errors/404.html'), 404


@app.get('/api/db/create-mysql-connection')
def runningRawSql():
    from sqlalchemy import create_engine, text

    engine = create_engine("mysql+pymysql://root:toor@localhost:3306/others_flask_demo")
    connection = engine.connect()
    query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY AUTO_INCREMENT, 
            name VARCHAR(100), 
            email VARCHAR(100), 
            phone VARCHAR(20), 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """

    query = """
        CREATE TABLE IF NOT EXISTS cities (
            id INT PRIMARY KEY AUTO_INCREMENT, 
            name VARCHAR(100), 
            code VARCHAR(100), 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """
    connection.execute(text(query))


    result = connection.execute(text("INSERT INTO users (name, email, phone) VALUES ('Varun Kumar', 'kumar92varun@gmail.com', '8826039646')"))
    connection.commit()

    result = connection.execute(text("UPDATE users set name = 'Varun' WHERE name = 'Varun Kumar'"))
    connection.commit()

    result = connection.execute(text("DELETE FROM users WHERE name = 'Varun'"))
    # connection.commit()


    connection.close()

    return {"engine": str(engine), "connection": str(connection), "result": str(result)}


@app.get('/api/db/select-records')
def runningSelectQuery():
    from sqlalchemy import create_engine, text

    engine = create_engine("mysql+pymysql://root:toor@localhost:3306/others_flask_demo")
    connection = engine.connect()

    result = connection.execute(text("SELECT * FROM users"))
    oneRecord = result.fetchone()
    print("Dumping 'oneRecord' object:")
    print(oneRecord)
    print(type(oneRecord))
    print("Printing one record:")
    print(f"Name: {oneRecord.name}, Email: {oneRecord.email}, Phone: {oneRecord.phone}")

    oneRecord = result.fetchone()
    print("Dumping 'oneRecord' object:")
    print(oneRecord)
    print(type(oneRecord))
    print("Printing one record:")
    print(f"Name: {oneRecord.name}, Email: {oneRecord.email}, Phone: {oneRecord.phone}")


    # result = connection.execute(text("SELECT * FROM users"))
    allRecords = result.fetchall()
    print("Dumping 'allRecords' object:")
    print(allRecords)
    print(type(allRecords))
    print("Printing all records:")
    for record in allRecords:
        print(f"Name: {record.name}, Email: {record.email}, Phone: {record.phone}")