#!/usr/bin/python3

from flask import Flask, abort, request
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
	if user is None:
		abort(404)
	return json.dumps({'id': user.id, 'name': user.name})

# "/users/<int:user_id>" weglaten en ingelogde id gebruiken
@app.route("/users/<int:user_id>/tests/my")
def get_user_tests(user_id):
	tests = session.query(model.Test).filter_by(user_id=user_id).all()
	if tests is None:
		abort(404)
	json_tests = []
	for test in tests:
		json_tests.append({'id': test.id, 'name': test.name, 'last_ok': test.last_ok, 'data': test.data})
	return json.dumps(json_tests)

@app.route("/users/<int:user_id>/tests/add", methods=['POST'])
def add_user_test(user_id):
	if 'name' in request.form and 'data' in request.form:
		session.add(model.Test(user_id=-user_id, name=request.form['name'], data=request.form['data']))
		return json.dumps({'success': True})
	else:
		return json.dumps({'success': False, 'error': 'Missing data'})

@app.route("/tests/<int:test_id>")
def get_test_by_id(test_id):
	test = session.query(model.Test).get(test_id)
	if test is None:
		abort(404)
	return json.dumps({'id': test.id, 'name': test.name, 'last_ok': test.last_ok, 'data': test.data})

app.run()
