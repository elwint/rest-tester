#!/usr/bin/python3

from flask import Flask, abort, request, g
from sqlalchemy import Integer
import json
import string
import random

from db import session
import data
import model
import crypt

app = Flask("rest-tester")
app.config['PROPAGATE_EXCEPTIONS']=True

@app.after_request
def set_header(response):
	response.headers["Content-Type"] = "application/json"
	response.headers["Access-Control-Allow-Origin"] = "*"
	response.headers["Access-Control-Allow-Method"] = "OPTIONS, GET, POST, PUT, DELETE"
	response.headers["Access-Control-Allow-Headers"] = "Token, Content-Type"
	return response

@app.before_request
def check_token():
	if request.method == "OPTIONS":
		return ""
	if request.path == "/login":
		return None
	token = request.headers.get("Token")
	if token == None or token == "":
		abort(400)

	try:
		auth = session.query(model.Token).filter_by(token=token).one()
	except Exception:
		abort(403)

	g.user_id = auth.user_id

@app.errorhandler(500)
def internal_server_error(error):
	return '"Internal server error"', 500

@app.errorhandler(404)
def page_not_found(error):
	return '"Resource not found"', 404

@app.errorhandler(403)
def unauthorized(error):
	return '"Access denied"', 403

@app.errorhandler(400)
def bad_request(error):
	return '"Bad request"', 400


TOKEN_CHARS = string.ascii_lowercase + string.ascii_uppercase + string.digits

@app.route("/login", methods=['POST'])
def login():
	input_data = request.get_json()
	username = input_data['user']
	if username == None or username == '':
		abort(400)
	password = input_data['pass']
	if password == None or password == '':
		abort(400)

	user = session.query(model.User).filter(model.User.name.ilike(username)).first()
	if user == None:
		abort(404)
	if not crypt.check(password, user.password):
		abort(403)

	token = ''.join(random.SystemRandom().choice(TOKEN_CHARS) for _ in range(100))
	session.add(model.Token(user_id=user.id, token=token))

	return json.dumps(token)

@app.route("/users/<int:user_id>", methods=['GET'])
def get_user_by_id(user_id):
	user = session.query(model.User).get(user_id)
	if user == None:
		abort(404)
	return json.dumps({"id": user.id, "name": user.name})

@app.route("/tests/<int:test_id>", methods=['GET'])
def get_test_by_id(test_id):
	test = check_test_access(test_id, False)
	return json.dumps(test.data)

@app.route("/tests/mine", methods=['GET'])
def get_my_tests():
	tests = session.query(model.Test).filter(model.Test.data["user_id"].astext.cast(Integer) == g.user_id).all()

	out = []
	for test in tests:
		out.append(test.data)
	return json.dumps(out)

@app.route("/tests", methods=['POST'])
def add_test():
	input_data = request.get_json()
	if 'name' not in input_data or 'autorun_time' not in input_data or 'data' not in input_data:
		abort(400)

	last_test = session.query(model.Test).order_by(model.Test.data["id"].astext.desc()).first()
	if last_test == None:
		test_id = 0
	else:
		test_id = last_test.data['id'] + 1
	test = model.Test(data={
		"id": test_id,
		"user_id": g.user_id,
		"name": input_data['name'],
		"last": {
			"ok": None,
			"time": None
		},
		"shared_with": [],
		"autorun_time": input_data['autorun_time'],
		"group": input_data.get('group', None), # Optional
		"data": input_data['data']
	})
	session.add(test)
	return json.dumps({"id": test_id}), 201

@app.route("/tests/<int:test_id>", methods=['PUT'])
def update_test(test_id):
	input_data = request.get_json()
	test = check_test_access(test_id, True)

	count = session.query(model.Test).filter(model.Test.data["id"].astext.cast(Integer)==test_id).update({"data": {
		"id": test_id,
		"user_id": g.user_id,
		"name": input_data.get('name', test.data['name']),
		"last": test.data['last'],
		"shared_with": input_data.get('shared_with', test.data['shared_with']),
		"autorun_time": input_data.get('autorun_time', test.data['autorun_time']),
		"group": input_data.get('group', test.data['group']),
		"data": input_data.get('data', test.data['data']),
	}}, synchronize_session=False)
	if count == 0:
		abort(500)
	return json.dumps({"status": "ok"})

@app.route("/tests/<int:test_id>", methods=['DELETE'])
def delete_test(test_id):
	check_test_access(test_id, True)
	count = session.query(model.Test).filter(model.Test.data["id"].astext.cast(Integer)==test_id).delete(synchronize_session=False)
	if count == 0:
		abort(500)
	return json.dumps({"status": "ok"})

@app.route("/tests/<int:test_id>/history", methods=['GET'])
def get_test_history_by_id(test_id):
	check_test_access(test_id, False)
	history = session.query(model.History).filter(model.History.data["test_id"].astext.cast(Integer) == test_id).all()

	out = []
	for h in history:
		out.append({"ok": h.data['ok'], "time": h.data['time']})
	return json.dumps(out)

def check_test_access(test_id, owner_only=False):
	test = session.query(model.Test).filter(model.Test.data["id"].astext.cast(Integer)==test_id).first()
	if test == None:
		abort(404)
	if test.data['user_id'] == g.user_id:
		return test
	if not owner_only and g.user_id in test.data['shared_with']:
		return test
	abort(403)

app.run()
