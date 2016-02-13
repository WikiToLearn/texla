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



def get_environment_greedy(tex, env):
	'''
	This functions extract the env environment in a greedy way.
	It finds nested environment with same env.
	It return the start and end pos of the environment 
	and the string matched with \\begin and \\end
	'''
	begin = '\\begin{'+ env+'}'
	end = '\\end{'+ env + '}'
	bre = re.compile(r'\\begin{'+ env+'}')
	ere = re.compile(r'\\end{'+ env + '}')
	matchs = {}
	pos = {}
	for bmatch in bre.finditer(tex):
		matchs[bmatch.start()] = bmatch
		pos[bmatch.start()] = 'begin'
	for ematch in ere.finditer(tex):
		matchs[ematch.start()]= ematch
		pos[ematch.start()] = 'end'
	#now I cycle through dictionary in ordered mode.
	#I'm assuming that the first item is a begin one
	level = 0
	start_match = None
	end_match = None
	od = collections.OrderedDict(sorted(pos.items()))
	for k,v in od.items():
		if v == 'begin':
			if level ==0:
				start_match = matchs[k]
			level+=1
		else:
			level-=1
			if level == 0:
				end_match = matchs[k]
		#check the level
		if level == 0:
			#we can return the start, end pos and the matches itself
			return (start_match.start(), end_match.end(),
					 tex[start_match.start(): end_match.end()])


def get_environment_content_greedy(tex,env):
	'''
	This funciont returns the content of the environment 
	in a greedy way
	'''
	begin = '\\begin{'+ env+'}'
	end = '\\end{'+ env + '}'
	bre = re.compile(r'\\begin{'+ env+'}')
	ere = re.compile(r'\\end{'+ env + '}')
	matchs = {}
	pos = {}
	for bmatch in bre.finditer(tex):
		matchs[bmatch.start()] = bmatch
		pos[bmatch.start()] = 'begin'
	for ematch in ere.finditer(tex):
		matchs[ematch.start()]= ematch
		pos[ematch.start()] = 'end'
	#now I cycle through dictionary in ordered mode.
	#I'm assuming that the first item is a begin one
	level = 0
	start_match = None
	end_match = None
	od = collections.OrderedDict(sorted(pos.items()))
	for k,v in od.items():
		if v == 'begin':
			if level ==0:
				start_match = matchs[k]
			level+=1
		else:
			level-=1
			if level == 0:
				end_match = matchs[k]
		#check the level
		if level == 0:
			#we can return the start, end pos and the matches itself
			return tex[start_match.end(): end_match.start()]


def get_command_greedy(tex):
	'''This function removes the first command found in
	the string. It removes all its parenthesis in a greedy way.
	If the string is '\emph[option]{text}\emph{..}' it removes the 
	first command. 
	It returns a tuple with the extracted command with options , the 
	command itself (only the name), the remaining tex and it's 
	starting index). 
	Example: (cmd_tex, cmd, left_tex, left_tex starting index)
	If there are no commands it returns the tex as 
	(tex, '', '' len(tex)) for consistency.
	'''
	logging.debug('UTILITY.get_command_greedy @ tex: %s', tex)
	#first of all we remove the cmd 
	re_cmd = re.compile(r'\\(?P<cmd>.*?)[\[\{]')
	#we match the fist command
	mat = re_cmd.search(tex)
	if mat ==None:
		logging.debug('UTILITY.get_command_greedy @ any command found!')
		return (tex,'','',len(tex))
	cmd = mat.group('cmd')
	left_tex = tex[mat.end('cmd'):]
	#now we extract the tokens
	toks = remove_parenthesis(left_tex)
	result = '\\'+cmd 
	for t, cont ,e in toks:
		if t != 'out':
			result+= t+cont+e
	return (result, cmd, left_tex[len(result):], len(result))


def remove_parenthesis(tex):
	'''This funcion parses strings like '[text]{text}[text]..'
	It parses only [ and { parenthesis. It returns a list of tuples
	in the format: (start_parenthesis, content , end_parenthesis).
	The remaining string, not in [] or {}, is returned as ('out', string, '').
	The function is able to understand nested parenthesis.
	'''
	if tex.startswith('['):
		beginp = '['
		endp = ']'
	elif tex.startswith('{'):
		beginp = '{'
		endp = '}'
	else:
		#if the tex doesn't start
		#with [ or { a empty list is returnses
		return [('out',tex,'')]
	content= []
	level = 0
	pos = -1
	for ch in tex:
		pos+=1
		if ch == beginp:
			level+=1
		elif ch == endp:
			level-=1
		if level==0:
			#we can extrac the token
			content.append((beginp, tex[1:pos], endp))
			break
	#the left tex is parsed again
	content += remove_parenthesis(tex[pos+1:])
	return content


