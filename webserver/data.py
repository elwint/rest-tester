import model
import crypt
from db import session

session.add(model.User(name='Bassie', password=crypt.hash('abc')))
session.add(model.User(name='Tester', password=crypt.hash('def')))
session.add(model.Token(user_id=1, token="test"))

session.add(model.Test(data={
	"id": 1,
	"user_id": 1,
	"name": "Test 1",
	"last": {
		"ok": True,
		"elapsed_time": 16,
		"timestamp": 1496836918
	},
	"shared_with": [],
	"autorun_time": -1,
	"group": None,
	"data": {}
}))
session.add(model.Test(data={
	"id": 2,
	"user_id": 2,
	"name": "Test 2",
	"last": {
		"ok": None,
		"elapsed_time": None,
		"timestamp": None
	},
	"shared_with": [1],
	"autorun_time": -1,
	"group": None,
	"data": {}
}))
session.add(model.History(data={
	"test_id": 1,
	"ok": False,
	"elapsed_time": 337,
	"timestamp": 1496836917
}))
session.add(model.History(data={
	"test_id": 1,
	"ok": True,
	"elapsed_time": 16,
	"timestamp": 1496836918
}))
session.flush()
