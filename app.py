from flask import Flask

app = Flask(__name__)

@app.route('/')
def homePage():
    return "Varun Kumar is great"


@app.route('/<name1>')
def javascript(name1):
    return f"<script>alert('Hiiii from {name1}');console.log('Hiiii from {name1}');</script><body>Hiii from {name1}</body>"


@app.route('/json')
def jsonResponse():
    return {
        "name": "Varun Kumar"
    }