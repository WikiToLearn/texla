import random

def get_random_string(N):
	return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))