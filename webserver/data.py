import model
import crypt
from db import session

session.add(model.User(name='Bassie', password=crypt.hash('abc')))
session.add(model.User(name='Tester', password=crypt.hash('def')))
session.add(model.Token(user_id=1, token="test"))

session.add(model.Test(data={
	"id": 1,
	"version": 1,
	"user_id": 1,
	"name": "Test 1",
	"last": {
		"ok": True,
		"status": 200,
		"elapsed_time": 16,
		"timestamp": 1496836918
	},
	"shared_with": [],
	"autorun": "never",
	"group": None,
	"data": {}
}))
session.add(model.Test(data={
	"id": 2,
	"version": 1,
	"user_id": 2,
	"name": "Test 2",
	"last": {},
	"shared_with": [1],
	"autorun": "every_day",
	"group": None,
	"data": {}
}))
session.add(model.Test(data={
	"id": 3,
	"version": 1,
	"user_id": 1,
	"name": "Test 3",
	"last": {
		"ok": False,
		"status": 200,
		"elapsed_time": 85,
		"timestamp": 1496836920
	},
	"shared_with": [],
	"autorun": "never",
	"group": None,
	"data": {}
}))
session.add(model.Test(data={
	"id": 4,
	"version": 2,
	"user_id": 1,
	"name": "Test 4",
	"last": {},
	"shared_with": [],
	"autorun": "never",
	"group": None,
	"data": {}
}))
session.add(model.History(data={
	"test_id": 1,
	"version": 1,
	"ok": True,
	"status": 500,
	"elapsed_time": 337,
	"timestamp": 1496836917
}))
session.add(model.History(data={
	"test_id": 1,
	"version": 1,
	"ok": True,
	"status": 200,
	"elapsed_time": 16,
	"timestamp": 1496836918
}))
session.flush()
