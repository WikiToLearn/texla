import re
import collections
import logging
import string

'''
This module provides some utility function for environments
parsing
'''

def get_environment(tex, env):
	'''
	This functions extract the env environment in a greedy way.
	It finds nested environment with same env.
	It return the start and end pos of the environment
	and the string matched inside \\begin and \\end
	'''
	begin = '\\begin{(?: *)' + env+'(?: *)}'
	end = '\\end{(?: *)'+ env + '(?: *)}'
	bre = re.compile(r'\\begin{(?: *)'+ env+'(?: *)}')
	ere = re.compile(r'\\end{(?: *)'+ env + '(?: *)}')
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
			#without the \begin{}, \end{} part.
			return (start_match.start(), end_match.end(),
					 tex[start_match.end(): end_match.start()])


def get_environment_content(tex,env):
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
