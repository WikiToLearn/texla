import random

section_level = {
	'root' = -1,
	'part' = 0,
	'chapter' = 1,
	'section' = 2,
	'subsection' = 3,
	'subsubsection' = 4,
	'paragraph' = 5,
	'subparagraph' = 6
}

def get_random_string(N):
	return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))