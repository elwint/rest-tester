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
	username = request.form.get('user')
	if username == None or username == '':
		abort(400)
	password = request.form.get('pass')
	if password == None or password == '':
		abort(400)

	user = session.query(model.User).filter(model.User.name.ilike(username)).first()
	if not crypt.check(password, user.password):
		abort(403)

	token = ''.join(random.SystemRandom().choice(TOKEN_CHARS) for _ in range(100))
	session.add(model.Token(user_id=user.id, token=token))

	return json.dumps(token)

@app.route("/users/<int:user_id>")
def get_user_by_id(user_id):
	user = session.query(model.User).get(user_id)
	if user == None:
		abort(404)
	return json.dumps({'id': user.id, 'name': user.name})

@app.route("/tests/<int:test_id>")
def get_test_by_id(test_id):
	test = session.query(model.Test).get(test_id, user_id=g.user_id)
	if test is None:
		abort(404)
	return json.dumps({'id': test.id, 'name': test.name, 'last_ok': test.last_ok, 'data': test.data})

@app.route("/tests/mine")
def get_my_tests():
	print(g.user_id)
	tests = session.query(model.Test).filter_by(user_id=g.user_id).all()

	out = []

	for test in tests:
		out.append({"id": test.id, "name": test.name, 'last_ok': test.last_ok, 'data': test.data})
	return json.dumps(out)

@app.route("/tests", methods=['PUT'])
def add_test():
	if not 'name' in request.form or not 'data' in request.form:
		abort(400)

	session.add(model.Test(user_id=g.user_id, name=request.form.get('name'), data=request.form.get('data')))
	return json.dumps({"status": "ok"})

app.run()
