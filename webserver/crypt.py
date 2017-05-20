import bcrypt

def hash(password):
	return bcrypt.hashpw(password.encode('ascii'), bcrypt.gensalt(13))
