#!/usr/bin/python3

from flask import Flask, abort
import json

from db import session
import data
import model

app = Flask("rest-tester")
app.config['PROPAGATE_EXCEPTIONS']=True

@app.after_request
def apply_caching(response):
	response.headers["Content-Type"] = "application/json"
	return response

@app.errorhandler(404)
def page_not_found(error):
	return '"Resource not found"', 404

@app.route("/users/<int:user_id>")
def get_user_by_id(user_id):
	user = session.query(model.User).filter_by(id=user_id).first()
	if user == None:
		abort(404)
	return json.dumps({'id': user.id, 'name': user.name})

app.run()
