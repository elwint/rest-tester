#!/bin/python3
from flask import Flask
app = Flask("rest-tester")

@app.route("/")
def index():
	return "Hello World"

app.run()
