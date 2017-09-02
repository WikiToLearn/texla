'''
This module provides functions to parse commands and
their options
'''
import re
import logging
from . import utility

def parse_options(tex, grammar):
	'''
	This function extract commands options given a grammar.
	The tex input must start with the options parenthesis [ or {,
	and must not contain the \cmd part.
	The grammar is a list of tuples that defines the possible
	option for the command:
	[(opt_name, '{', '}' ), (opt_name2, '[', ']'),...  ].
	The function search for matches from left to right.
	A list of options is extracted from the tex, then
	a match is performed on the grammar: if the first grammar rule
	doesn't match the second one is checked, and so on for
	all parsed parenthesis.
	The function returns a dictionary with the matched
	options. If an option is not matched it returnrs None
	'''
	prt = get_parenthesis(tex)
	#now we have to match the parenthesis with the grammar,
	#preloading keys with None
	result = {x[0]:None  for x in grammar}
	left_tex = ''
	#preloading of void options
	for pr in prt:
		beginp = pr[0]
		content = pr[1]
		endp = pr[2]
		if beginp=='out':
			left_tex = content
		#now we have to check the grammar
		for gr in enumerate(grammar):
			name = gr[1][0]
			start_p = gr[1][1]
			end_p = gr[1][2]
			if start_p==beginp and end_p == end_p:
				#ok the option is found
				result[name] = content
				#this grammar item is removes
				grammar.pop(gr[0])
				break
			else:
				result[name] = None
	return (result, left_tex)

def get_command_options(tex):
	'''
	The function removes an arbitrary number of options
	parenthesis from tex.
    The funcion is useful to remove a command's
	parenthesis without knowing their structure.
	The function return (matched parenthesis, left tex,
	starting index of left tex ).
    The tex could also have not parenthesis.
	'''
	#now we extract the tokens
	toks = get_parenthesis(tex)
	result = ''
	for t, cont ,e in toks:
		if t != 'out':
			result+= t+cont+e
	return (result, tex[len(result):], len(result))


def get_parenthesis(tex):
    '''This funcion parses strings like '[text]{text}(text)..'
    It parses only (, [ and { parenthesis. It returns a list of tuples
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
    elif tex.startswith('('):
        beginp = '('
        endp = ')'
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
    content += get_parenthesis(tex[pos+1:])
    return content

def get_command_greedy(tex):
	'''
	This function removes the first command found in
	the string (the string must start with the command).
	It removes all its parenthesis in a greedy way.
	If the string is '\emph[option]{text}\emph{..}' it removes the
	first command.
	It returns a tuple with the extracted command name, the command content
	with options, the remaining	tex and it's starting index).
	Example: (cmd,  cmd_tex, left_tex, left_tex starting index)
	If there are no commands it returns the tex as
	(tex, '', '', len(tex)) for consistency.
	'''
	logging.debug('COMMAND_PARSER.get_command_greedy @ tex: %s', tex)
	#first of all we remove the cmd
	re_cmd = re.compile(r'\\(?P<cmd>.*?)[\[\{]')
	#we match the fist command
	mat = re_cmd.match(tex)
	if mat ==None:
		logging.debug('COMMAND_PARSER.get_command_greedy @ any command found!')
		return (tex,'','',len(tex))
	cmd = mat.group('cmd')
	left_tex = tex[mat.end('cmd'):]
	#now we extract the tokens
	toks = get_parenthesis(left_tex)
	result = '\\'+cmd
	for t, cont ,e in toks:
		if t != 'out':
			result+= t+cont+e
	return (cmd, result, tex[len(result):], len(result))
