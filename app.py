from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.get('/mct/welcome')
def helloWorld():
    return " Welcome to Python Flask and Render"
