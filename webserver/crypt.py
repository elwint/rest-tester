import bcrypt

def hash(password):
	return bcrypt.hashpw(password.encode('ascii'), bcrypt.gensalt(13))

def check(password, hashed):
	return bcrypt.checkpw(password.encode('ascii'), hashed)
