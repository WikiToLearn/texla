import re
import collections
   

'''
This functions extract the env environment in a greedy way.
It finds nested environment with same env.
It return the start and end pos of the environment 
and the string matched with \\begin and \\end
'''
def get_environment_greedy(tex, env):
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
					 tex[start_match.end(): end_match.start()])




'''
This function split the given tex in text parts and environments.
Only the first level of environments is searched: the function don't 
go inside nested environments, the parser_cycle will manage this.

It return a list of tuples like:
[ ('text','abcde..) , ('itemize','\\begin{itemize}..\\end{itemize}' ,..)]
'''
def environments_tokenizer( tex):
	#list of tuple for results ('type_of_env', content)
	env_list= []
	#we search for the first enviroment
	re_env1 = re.compile(r'\\begin\{(?P<env>.*?)\}')
	match = re_env1.search(tex)
	if not match == None:
		#we save the first part without 
		env_list.append(('text',tex[0:match.start()]))
		#the remaing part with the first matched is analized
		tex = tex[match.start():]
		env = match.group('env')
		#now we extract the env greedy
		s,e,content = get_environment_greedy(tex,env)
		env_list.append((env, content))
		#now we iterate the process for remaining tex
		left_tex = tex[e:]
		#returning the ordered list of matches
		after_env_list = environments_tokenizer(left_tex)
		if not after_env_list==None:
			env_list = env_list + after_env_list
		return env_list


a = open('test_env.tex', 'r').read()

l = environments_tokenizer(a)

for i in l:
	print(i)