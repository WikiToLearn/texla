import random
import re
import collections
import logging
import string

section_level = {
   -1 : 'root',
	0 : 'part',
	1 : 'chapter',
	2 : 'section',
	3 : 'subsection',
	4 : 'subsubsection',
	5 : 'paragraph',
	6 : 'subparagraph'
}

def get_random_string(N):
	return ''.join(random.SystemRandom().choice(string.ascii_lowercase + \
		string.digits) for _ in range(N))
