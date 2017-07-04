#!/usr/bin/python3

from flask import Flask, abort, request, g
from sqlalchemy import Integer, not_
import json, string, random, time

from db import session
import model
if session.query(model.Test).count() == 0:
	import example_data
import crypt

app = Flask("rest-tester")
app.config['PROPAGATE_EXCEPTIONS']=True

TOKEN_CHARS = string.ascii_lowercase + string.ascii_uppercase + string.digits
AUTORUN_OPTIONS = ["never", "every_day", "every_week", "every_month"]
DATA_TYPES = {"json": "jsonpath_mini"}
DATA_COMPARATORS = {"equals": "str_eq", "exists": "exists"}

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
	return json.dumps(test)

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
	if 'name' not in input_data or 'autorun' not in input_data or 'data' not in input_data:
		abort(400)
	if input_data['autorun'] not in AUTORUN_OPTIONS or not validate_test_data(input_data['data']):
		abort(400)

	last_test = session.query(model.Test).order_by(model.Test.data["id"].astext.desc()).first()
	if last_test == None:
		test_id = 1
	else:
		test_id = last_test.data['id'] + 1
	test = model.Test(data={
		"id": test_id,
		"version": 1,
		"user_id": g.user_id,
		"name": input_data['name'],
		"last": {},
		"shared_with": [],
		"autorun": input_data['autorun'], # "never", "every_day", "every_week", "every_month"
		"group": input_data.get('group', None), # Optional
		"data": input_data['data']
	})
	session.add(test)
	return json.dumps({"id": test_id}), 201

@app.route("/tests/<int:test_id>", methods=['PUT'])
def update_test(test_id):
	input_data = request.get_json()
	if 'autorun' in input_data and input_data['autorun'] not in AUTORUN_OPTIONS:
		abort(400)
	if 'data' in input_data and not validate_test_data(input_data['data']):
		abort(400)

	test = check_test_access(test_id, True)
	version = test['version']
	last = test['last']
	if 'data' in input_data and input_data['data'] != test['data']:
		version += 1
		last = {}
	count = session.query(model.Test).filter(model.Test.data["id"].astext.cast(Integer)==test_id).update({"data": {
		"id": test_id,
		"version": version,
		"user_id": g.user_id,
		"name": input_data.get('name', test['name']),
		"last": last,
		"shared_with": input_data.get('shared_with', test['shared_with']),
		"autorun": input_data.get('autorun', test['autorun']),
		"group": input_data.get('group', test['group']),
		"data": input_data.get('data', test['data']),
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
		out.append({"version": h.data['version'], "ok": h.data['ok'], "status": h.data['status'], "elapsed_time": h.data['elapsed_time'], "timestamp": h.data['timestamp']})
	return json.dumps(out)

def check_test_access(test_id, owner_only=False):
	test = session.query(model.Test).filter(model.Test.data["id"].astext.cast(Integer)==test_id).first()
	if test == None:
		abort(404)
	if test.data['user_id'] == g.user_id:
		return test.data
	if not owner_only and g.user_id in test.data['shared_with']:
		return test.data
	abort(403)

@app.route("/tests/<int:test_id>", methods=['POST'])
def run_test(test_id):
	current_test = check_test_access(test_id, True)

	# Run test
	timestamp = int(time.time())
	time.sleep(random.choice([0.1, 0.2, 0.3, 0.4, 0.5]))
	ok = random.choice([True, False])
	status = random.choice([200, 500, 404, 403])
	elapsed_time = random.choice([20, 213, 399, 443])

	test = check_test_access(test_id, True) # Only update last if version is still the same
	if current_test['version'] == test['version']:
		count = session.query(model.Test).filter(model.Test.data["id"].astext.cast(Integer) == test_id).update(
			{"data": {
				"id": test_id,
				"version": test['version'],
				"user_id": g.user_id,
				"name": test['name'],
				"last": {
					"ok": ok,
					"status": status,
					"elapsed_time": elapsed_time,
					"timestamp": timestamp
				},
				"shared_with": test['shared_with'],
				"autorun": test['autorun'],
				"group": test['group'],
				"data": test['data'],
			}}, synchronize_session=False)
		if count == 0:
			abort(500)

	h = model.History(data={
		"test_id": test_id,
		"version": current_test['version'],
		"ok": ok,
		"status": status,
		"elapsed_time": elapsed_time,
		"timestamp": timestamp
	})
	session.add(h)
	return json.dumps({"version": current_test['version'], "ok": ok, "status": status, "elapsed_time": elapsed_time, "timestamp": timestamp}), 201

def autorun_tests(): # TODO
	tests = session.query(model.Test).filter(not_(model.Test.data["autorun"].astext == "never")).all()

def validate_test_data(test_data):
	if 'method' not in test_data or 'url' not in test_data or 'status' not in test_data:
		return False
	if test_data["method"] != "GET" and 'body' not in test_data:
		return False
	if 'extract' in test_data:
		for extract in test_data["extract"]:
			if 'type' not in extract or 'key' not in extract or 'variable' not in extract:
				return False
			if extract['type'] not in DATA_TYPES:
				return False
	if 'checks' in test_data:
		for check in test_data["checks"]:
			if 'type' not in check or 'key' not in check or 'compare' not in check:
				return False
			if check['type'] not in DATA_TYPES:
				return False
			if check['compare'] not in DATA_COMPARATORS:
				return False
			if check['compare'] != "exists" and 'value' not in check:
				return False
	return True

def parse_to_yaml(tests_data):
	yaml = ""
	bind_vars = []
	for test_data in tests_data:
		yaml += "- test\n" \
				"	- url: " + test_data["url"] + "\n" \
				"	- method: '" + test_data["method"] + "'\n"
		if "body" in test_data:
			yaml += "	- body: '" + test_data["body"] + "'\n" + \
					"	- headers: : {Content-Type: application/json}\n"
		yaml += "	- expected_status: [" + test_data["status"] + "]\n"
		if "extract" in test_data and test_data["extract"]:
			yaml += "	- extract_binds:\n"
			for extract in test_data["extract"]:
				yaml += "		- '" + extract["variable"] + "': {" + DATA_TYPES[extract["type"]] + ": '" + extract["key"] + "'}\n"
				bind_vars.append(extract["variable"])
		if "checks" in test_data and test_data["checks"]:
			yaml += "	- validators:\n"
			for check in test_data["checks"]:
				if check["compare"] == "exists":
					yaml += "		- extract_test: {" + DATA_TYPES[check["type"]] + ": '" + check["key"] + "', test: 'exists'}\n"
				else:
					if check["value"] in bind_vars:
						expected = "{template: '$" + check["value"] + "'}"
					else:
						expected = "'" + check["value"] + "'"
					yaml += "		- compare: {" + DATA_TYPES[check["type"]] + ": '" + check["key"] + "', comparator: '" + DATA_COMPARATORS[check["compare"]] + "', expected: " + expected + "}\n"
	return yaml

app.run()
