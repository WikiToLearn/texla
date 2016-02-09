import os
import re

class Parser:

	def __init__(self):
		pass


	def parse(self,tex):
		###TODO:preparsing

		#Getting content of 
		m_doc = regexes.r_doc.search(tex)
		#getting content
		content = m_doc.groups("content")
		options = m_doc.groups("options")
		#creating root block
		self.root_block = documentBlock()
		#beginning of parsing 
		self.parser_cycle(self.root_block,content)


'''
A parser cycle needs a prent block, the tex to parser and
a dictionary of options.
options contains:
-parser_sections: say if the parser has to call parser_sections()
-next_sec_level: this parameter says to parser_sections()
	what level of sections has to be splitted


'''
	def parser_cycle(self, parent_block, tex, options):
		#first of all we search for sectioning


'''
This parser function search for sections splitting inside tex.
The level of sections searched is indicated by level.
The function calls the parser_hooks of every section block.
'''
    def parse_sections(self, parent_block, tex, level):
    	#check if the level is greater than subparagraph
    	if (level+1) < (len(utility.section_level)-1):
    		level_key = utility.section_level[level+1]
    		sec_re = re.compile(r'\\'+ level_key)
    		#the tex is splitted by the section key
    		toks = sec_re.split(tex)
    		#the first token is the tex outside sectioning
    		outside_sec = toks.pop(0)
    		#this tex has to be parser but with a sectioning
    	    #level greater than one
    		self.parser_cycle(parent_block,outside_sec, 
    					options['next_sec_level']+=1)
    		#now the sections found are processed
    		for tok in toks:
    			#readding splitted command
    			tok = '\\'+ level_key +tok
    			new_block = self.parser_hooks[level_key](tok, parent_block)
    			#adding new_block to the parent block
    			parent_block.add_children_block(new_block)


    def parse_environments(self, parent_block, tex, options):
    	#first of all

    
	def environments_tokenizer(tex):
    	#list of tuple for results ('type_of_env', content)
    	env_list= []
    	#we search for the first enviroment
    	re_env1 = re.compile(r'\\begin\{(?P<env>.*?)\}')
    	match = re_env1.search(tex)
    	if not match == None:
    		#we save the first part without 
    		env_list.append(('tex',tex[0:match.start()]))
    		#the remaing part with the first matched is analized
    		tex = tex[match.start():]
    		env = match.group('env')
    		#now we extract the env greedy
    		s,e,content = utility.get_environment_greedy(tex,env)
    		env_list.append((env, content))
    		#now we iterate the process for remaining tex
    		left_tex = tex[e:]
    		#returning the ordered list of matches
    		after_env_list = self.environments_tokenizer(left_tex)
    		if not after_env_list==None:
    			env_list = env_list + after_env_list
    		return env_list








	def import_block_modules(self):
		self.parser_hooks={}
		for module in os.listdir("Blocks"):
			__import__(module)
			if hasattr(module,"parser_hooks"):
				for key,value  in module.parser_hooks.items():
					self.parser_functions[key] = value



