import os
import re

class Parser:

	def __init__(self):
		self.import_block_modules()


	def parse(self,tex):
		###TODO:preparsing
        #reading title...
        #reading author...

		#Getting content of 
		m_doc = regexes.r_doc.search(tex)
		#getting content
		content = m_doc.groups("content")
		options = m_doc.groups("options")
		#creating root block
		self.root_block = documentBlock('',{})
		#beginning of parsing 
        options = {'parse_sections':True,
                   'parse_environments':True,
                   'sec_level':0}
		blocks = self.parser_cycle(self.root_block,content,options)
        print (blocks)


	'''
    MAIN ENTRYPOINT FOR PARSING
	A parser cycle needs a parent block, the tex to parser and
	a dictionary of options.
	Options controls the flow of operations in this order:
    section-->environments-->math-->commands.
    Options dict contains:
	-parse_sections: say if the parser has to call parse_sections()
	-sec_level: this parameter says to parser_sections()
		what level of sections has to be splitted
    -parse_envs: say if the parser has to call parse_enviroments()
    -parse_math: parser call parse_math()
    -parse_commands: parser calls parse_commands()

    It returns a liste of tuples with the blocks parser, like:
    [('math',math_block ), ('emph', emph_block),..]

    The caller of the parser will manage to add the blocks to 
    the parent_block. The parend_block is passed as parameter 
    because it could contains useful informations for the parsing.

	'''
	def parser_cycle(self, tex, parent_block, options):
        #list for result
        parsed_blocks = []
		#first of all we search for sectioning if enables
        if options['parse_sections']:
            parsed_blocks+=self.parse_sections(tex, parent_block, options)
        #then we parse environments
        elif options['parse_envs']:
            parsed_blocks+=self.parse_environments(tex, parent_block, options)
        elif options['parse_math']:
            #then we parse maths
            parsed_blocks+=self.parse_math(tex, parent_block, options)
        elif options['parse_commands']:
            #finally single command are parserd
            parsed_blocks+=self.parse_commands(tex, parent_block, options)
        return parsed_blocks


	'''
	This parser function search for sections splitting inside tex.
	The level of sections searched is indicated by sec_level option.
	The function calls the parser_hooks of every section block.

    It returns a list of blocks parsed as tuples.
	'''
    def parse_sections(self, tex, parent_block, options):
        pblocks = []
        level = options['sec_level']
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
            new_options = options.copy()
            new_options['sec_level']+=1
    		pblocks+=self.parser_cycle(outside_sec, parent_block, new_options)
    		#now the sections found are processed
    		for tok in toks:
    			#readding splitted command
    			tok = '\\'+ level_key +tok
                #we insert the level in the options
                sec_options = { 'sec_level' : (level +1),
                            'level_key' : level_key }
                #the tuple with the result is saved
    			pblocks.append(self.call_parser_hook(level_key, tok, 
                                 parent_block, sec_options))
    	#found block are returned to main cycle
        return pblocks		


   '''
   This parser function parse the environments in a given tex.
   It uses environments_tokenizer to split tex inside text and env items.
   Then, text is send to another parser_cycle for further parsing.
   Envirnments block are processed by dedicated parser_hooks and 
   then returned as a list of tutle to parser_cycle()
   '''
    def parse_environments(self, tex, parent_block, options):
        pblocks = []
    	#first of all we get all the environment at first 
    	#level in the tex.
    	env_list = self.environments_tokenizer(tex)
    	#now we can further analyze text tokens
    	#and elaborate with parser_hooks the environment founded
    	for e in env_list:
    		if e[0] == 'text':
    			#we make sure that the section check is disabled
    			#because sectioning is parsed before environments
    			new_options = options.copy()
    			new_options['parse_sections'] = False
    			pblocks+=self.parser_cycle(e[1], parent_block, new_options)
    		else:
    			env = e[0]
    			#we can call the parser hooks
    			pblocks.append(self.call_parser_hook(env, e[1],parent_block))
        return pblocks

    
    '''
    This function split the given tex in text parts and environments.
    Only the first level of environments is searched: the function don't 
    go inside nested environments, the parser_cycle will manage this.

    It return a list of tuples like:
    [ ('text','abcde..) , ('itemize','\\begin{itemize}..\\end{itemize}' ,..)]
    '''
	def environments_tokenizer(self, tex):
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
    		s,e,content = utility.get_environment_greedy(tex,env)
    		env_list.append((env, content))
    		#now we iterate the process for remaining tex
    		left_tex = tex[e:]
    		#returning the ordered list of matches
    		after_env_list = self.environments_tokenizer(left_tex)
    		if not after_env_list == None:
    			env_list = env_list + after_env_list
    		return env_list


    '''
    This function parse math out of the tex. It splits tex in 
    math and text tokens. Text is further analyzed by a new 
    parser_cycle, the math tokens are processed by parser_hooks.
    Then parsed blocks are returned as a list of tuple to the
    parser_cycle()
    '''
    def parse_math(self, tex, parent_block, options):
        pblocks = []
    	#first of all we section the tex in a list
    	#of tuples with (type, content).
    	toks = self.math_tokenizer(tex)
    	#now we can further analyze text tokens
    	#and elaborate with parser_hooks the math founded
    	for e in toks:
    		if e[0] == 'text':
    			#we make sure that the section and env check is disabled
                #because sectioning and envs are parsed before math
    			new_options = options.copy()
    			new_options['parse_sections'] = False
                new_options['parse_envs'] = False
    			pblocks+=self.parser_cycle(e[1], parent_block, new_options)
    		else:
    			env = e[0]
    			#we can call the parser hooks
    			pblocks.append(self.call_parser_hook(env, e[1],parent_block))
        return pblocks

    '''
    This function split the tex inside a list of tuples with
    (type, content). The type could be text, display_math, inline_math.
    The function is able to extract math inside \(...\) $...$ (inline) and
    inside \[...\] $$...$$ (display).
    '''
    def math_tokenizer(self,tex):
    	inline_re = re.compile(r'(?<![\$])\$([^$]+)\$(?!\$)', re.DOTALL)
    	display_re = re.compile(r'(?<![\$])\$\$([^$]+)\$\$(?!\$)', re.DOTALL)
    	inline_re2 = re.compile(r'\\\((.*?)\\\)',re.DOTALL)
    	display_re2 = re.compile(r'\\\[(.*?)\\\]', re.DOTALL)
    	#first of all we match a save the pos
    	pos = {}
    	for mi in inline_re.finditer(tex):
    		pos[mi.start()] = ('inline_math',mi)
    	for md in display_re.finditer(tex):
    		pos[md.start()] = ('display_math',md)
    	for mi2 in inline_re2.finditer(tex):
    		pos[mi2.start()] = ('inline_math',mi2)
    	for md2 in display_re2.finditer(tex):
    		pos[md2.start()] = ('display_math',md2)
    	#now we sort the dictionary
    	tokens = []
    	last_tex_index = 0
    	for start in sorted(pos.keys()):
    		end = pos[start][1].end()
    		typ = pos[start][0]
    		content = pos[start][1].group()
    		previous_tex = tex[last_tex_index : start]
    		tokens.append(('text', previous_tex))
    		#the last_tex_index is moved forward
    		last_tex_index = end
    		#the match is saved
    		tokens.append((typ, content))
    	return tokens


    ''' 
    This function parse single latex commands. Sectioning, environments
    and math are already parsed. The function find the first command and 
    call the proper parser_hook. The hook elaborate the command and returns
    the tex left to parse. Then the fuction is called recursively.
    Parsed commands are returned to parser_cycle() as a list of tuples.
    '''
    def parse_commands(self, tex, parent_block, options):
        pblocks = []
        re_cmd = re.compile(r"\\(?P<cmd>[a-zA-Z\\']+?)(?=\s|\{)", re.DOTALL)
        match = re_cmd.search(tex)
        if match!=None:
            text = tex[:match.start()]
            #The text here is completely parsed.
            #We have to create a text block
            pblocks.append(self.call_parser_hook('text', text, parent_block))
            #the matched command is parser by the parser_hook
            #and the remaining tex is returned as the second element of
            #a list. The first element is the parsed command.
            result = self.call_parser_hook(match.group('cmd'), tex[match.start():],
                        parent_block)
            tex_left = result[1]
            pblocks.append(result[0])
            #the left tex is parsed again
    	    pblocks+=self.parse_commands(tex_left, parent_block, options)
        else:
            #a text block is created
            pblocks.append(self.call_parser_hook('text', tex, parent_block))
        return pblocks


    '''
    This function check if the required parser_hook is avaiable,
    if not it calls th default hook
    '''
    def call_parser_hook(hook, tex, parent_block, options={}):
        if hook in self.parser_hooks:
            return self.parser_hooks[hook](self, tex, parent_block, options)
        else 
            #default hook is called
            return self.parser_hooks['default'](self, tex, parent_block, options)

    	

    '''
    This functions imports all the Blocks modules.
    Each module has a parser_hooks() functions that returns a dictionary
    of hooks with handling functions. This dictionary is inserted in 
    the self.parser_hooks dictionary
    '''
	def import_block_modules(self):
		self.parser_hooks={}
		for module in os.listdir("Blocks"):
			__import__(module)
			if hasattr(module,"parser_hooks"):
				for key,value  in module.parser_hooks.items():
					self.parser_functions[key] = value



