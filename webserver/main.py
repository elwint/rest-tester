#!/usr/bin/python3

from flask import Flask, abort, request, g
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

	if request.method in ['POST', 'PUT']:
		g.input_data = request.get_json()
		if g.input_data == None:
			g.input_data = {}

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

@app.route("/login", methods=["POST"])
def login():
	username = g.input_data['user']
	if username == None or username == '':
		abort(400)
	password = g.input_data['pass']
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
	test = session.query(model.Test).filter_by(id=test_id, user_id=g.user_id).first()
	if test == None:
		abort(404)
	return json.dumps({"id": test.id, "name": test.name, "last_ok": test.last_ok, "data": test.data})

@app.route("/tests/mine", methods=['GET'])
def get_my_tests():
	tests = session.query(model.Test).filter_by(user_id=g.user_id).all()

	out = []

	for test in tests:
		out.append({"id": test.id, "name": test.name, "last_ok": test.last_ok, "data": test.data})
	return json.dumps(out)

@app.route("/tests", methods=['POST'])
def add_test():
	if not 'name' in g.input_data or not 'data' in g.input_data:
		abort(400)

	test = model.Test(user_id=g.user_id, name=g.input_data['name'], data=g.input_data['data'])
	session.add(test)
	session.flush()
	return json.dumps({"id": test.id}), 201

@app.route("/tests/<int:test_id>", methods=['PUT'])
def update_test(test_id):
	if not 'name' in g.input_data or not 'data' in g.input_data:
		abort(400)

	count = session.query(model.Test).filter_by(user_id=g.user_id, id=test_id).update({"name": g.input_data['name'], "data": g.input_data['data']})
	if count == 0:
		abort(403)
	return json.dumps({"status": "ok"})

@app.route("/tests/<int:test_id>", methods=['DELETE'])
def delete_test(test_id):
	count = session.query(model.Test).filter_by(user_id=g.user_id, id=test_id).delete()
	if count == 0:
		abort(403)
	return json.dumps({"status": "ok"})

app.run()
