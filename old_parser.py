def parse_environments(self, tex, parent_block, options):
        '''
        This parser function parse the environments in a given tex.
        It uses environments_tokenizer to split tex inside text and env items.
        Then, text is send to another parser_cycle for further parsing.
        Envirnments block are processed by dedicated parser_hooks and 
        then returned as a list of tutle to parser_cycle().
        N.B.: the tex passed to parser hook is the CONTENT
        of the environment, without \begin{} and \end{} part.
        '''
        pblocks = []
        #first of all we get all the environment at first 
        #level in the tex.
        env_list = self.environments_tokenizer(tex)
        logging.debug('PARSER.ENVIRONMENTS: tokens: ' + str([x[0] for x in env_list]))
        #now we can further analyze text tokens
        #and elaborate with parser_hooks the environment founded
        for e in env_list:
            if e[0] == 'text':
                #Sections and envs discovery is disabled 
                #because we have found text
                new_options = options.copy()
                new_options['parse_sections'] = False
                new_options['parse_envs'] = False
                pblocks+=self.parser_cycle(e[2], parent_block, new_options)
            else:
                env = e[0]
                #the name of catched env is inserted in options
                #with the star param
                env_options = {'env':env, 'star':e[1]}
                #we can call the parser hooks.
                #N.B.: the tex passed to parser hook is the CONTENT
                #of the environment, without \begin{} and \end{} part.
                pblocks.append(self.call_parser_hook(env,'env', e[2],
                        parent_block, env_options))
                logging.info('PARSER.ENVIRONMENTS @ block: %s', str(pblocks[-1]))
        return pblocks

    
    def environments_tokenizer(self, tex):
        '''
        This function split the given tex in text parts and environments.
        Only the first level of environments is searched: the function don't 
        go inside nested environments, the parser_cycle will manage this.
        N.B.: the tex returned is only the CONTENT of the environment, 
        without \begin{} and \end{} part.

        It returns a list of tuples with parsed env. If the env is starred
        the second parameter returned is True:
        [ ('text',False, 'abcde..) , ('itemize',(True/False),'content' ,..)]
        '''
        #list of tuple for results ('type_of_env', content)
        env_list= []
        #we search for the first enviroment
        re_env1 = re.compile(r'\\begin\{(?: *)(?P<env>\w*?)'+\
                            r'(?P<star>[*]?)(?: *)\}')
        match = re_env1.search(tex)
        if not match == None:
            #we save the first part outside environment STRIPED
            outside_env = tex[0:match.start()].strip()
            if len(outside_env) >0:
                env_list.append(('text',False,outside_env))
            #the remaing part with the first env matched is analized
            text = tex[match.start():]
            env = match.group('env')
            star = True if match.group('star')!='' else False
            env_tot = env + '\*' if star else env
            #now we extract the env greedy, with L-STRIPED content
            s,e,content = utility.get_environment(text,env_tot)
            env_list.append((env, star, content.lstrip()))
            #we iterate the process for remaining tex (STRIPED)
            #if it's not empty
            left_tex = text[e:].strip()
            if len(left_tex)>0 :
                after_env_list = self.environments_tokenizer(left_tex)
                if len(after_env_list) > 0:
                    env_list += after_env_list
        else:
            #all remaining text
            #IMPORTANT: it couldn't be void because the section
            #content is STRIPPED
            env_list.append(('text',False, tex))
        return env_list


    def parse_commands(self, tex, parent_block, options):
        ''' 
        This function parse single latex commands. Sectioning, environments
        are already parsed. The function finds the first command and 
        call the proper parser_hook. The hook elaborate the command and returns
        the new Block and the tex left to parse. Then the fuction is called 
        recursively.
        Remaining tex is passed to parser_cycle to parse math and plain text.
        Parsed commands are returned to parser_cycle() as a list of tuples.
        WARNING: the call_parser_hook result is ALWAYS  a tuple with
        (new Block, tex left to parser). 
        '''
        pblocks = []
        re_cmd = re.compile(r"\\(?:(?P<cmd>[a-zA-Z']+)"+\
                r"(?P<star>[*]?)|(?P<n>\\))", re.DOTALL)
        match = re_cmd.search(tex)
        if match!=None:
            #The text before the cmd is extracted and STRIPED
            left_text = tex[:match.start()].strip()
            if len(left_text)>0:
                #We have to call the parser_cycle
                new_options = options.copy()
                new_options['parse_sections'] = False
                new_options['parse_envs'] = False
                new_options['parse_commands'] = False
                pblocks+=self.parser_cycle(left_text, 
                    parent_block, new_options)
            #managing match
            if match.group('cmd')!=None:
                matched_cmd = match.group('cmd')
                star = True if match.group('star')!='' else False
                logging.debug('PARSER.COMMANDS @ matched: %s', matched_cmd)
                #we insert the matched options in the dict for hooks
                opts = {'cmd':matched_cmd, 'star':star}
                #the text passed to hooks is LEFT-STRIPPED to remove
                #spaces between commands and options.
                #N.B the matched part is not sent to hook
                tex_to_parse = tex[match.end():].lstrip()
                #the matched command is parsed by the parser_hook
                #and the remaining tex is returned as the second element of
                #a list.  The first element is the parsed Block.
                result = self.call_parser_hook(matched_cmd,'cmd',
                        tex_to_parse, parent_block,opts)
                logging.info('PARSER.COMMANDS @ block: %s', str(result[0]))
                #the block is appended
                pblocks.append(result[0])
                #the remaining tex is STRIPED and starts
                #a new cyle in parser_commands
                tex_left = result[1].strip()
                if len(tex_left)>0:
                    #the left tex is parsed again if not null
                    pblocks+=self.parse_commands(tex_left, 
                        parent_block, options)
            
            else:
                #we have a \\ command
                matched_cmd = '\\'
                logging.debug('PARSER.COMMANDS @ matched: \\')
                tex_to_parse = tex[match.end():].lstrip()
                #we insert the matched options in the dict for hooks
                opts = {'cmd':'\\', 'star':False}
                #check if we have \\*
                if tex_to_parse.startswith('*'):
                    opts['star'] = True
                    tex_to_parse = tex_to_parse[1:]
                #parser_hook call
                result = self.call_parser_hook(matched_cmd,'cmd',
                        tex_to_parse, parent_block,opts)
                logging.info('PARSER.COMMANDS @ block: %s', str(result[0]))
                #the block is appended
                pblocks.append(result[0])
                #the remaining tex is STRIPED and starts
                #a new cyle in parser_commands
                tex_left = result[1].strip()
                if len(tex_left)>0:
                    #the left tex is parsed again if not null
                    pblocks+=self.parse_commands(tex_left,  
                        parent_block, soptions)
        else:
            #the remaining tex is passed to parser_cyle
            #to parse text and math
            new_options = options.copy()
            new_options['parse_sections'] = False
            new_options['parse_envs'] = False
            new_options['parse_commands'] = False
            pblocks+=self.parser_cycle(tex, parent_block, new_options)
        return pblocks


    def parse_math(self, tex, parent_block, options):
        '''
        This function parse math out of the tex. It splits tex in 
        math and text tokens. Text is further analyzed by a new 
        parser_cycle, the math tokens are processed by parser_hooks.
        Then parsed blocks are returned as a list of tuple to the
        parser_cycle()
        '''
        pblocks = []
        #first of all we section the tex in a list
        #of tuples with (type, content).
        toks = self.math_tokenizer(tex)
        logging.debug('PARSER.MATH: tokens: '+ str([x[0] for x in toks]))
        #now we can save plain tex block.s
        for e in toks:
            if e[0] == 'text':
                poptions = {'env':'text'}
                pblocks.append(self.call_parser_hook('text','env', 
                    e[1],parent_block,poptions))
            else:
                env = e[0]
                #we can call the parser hooks with found math.
                poptions = {'env': env}
                pblocks.append(self.call_parser_hook(env,'env', 
                        e[1], parent_block, poptions))
                logging.info('PARSER.MATH @ block: %s', str(pblocks[-1]))
        return pblocks

    
    def math_tokenizer(self,tex):
        '''
        This function split the tex inside a list of tuples with
        (type, content). The type could be text, display_math, inline_math.
        The function is able to extract math inside \(...\) $...$ (inline) and
        inside \[...\] $$...$$ (display).
        '''
        inline_re = re.compile(r'(?<![\$])\$(?P<m>[^$]+)\$(?!\$)', re.DOTALL)
        display_re = re.compile(r'(?<![\$])\$\$(?P<m>[^$]+)\$\$(?!\$)', re.DOTALL)
        inline_re2 = re.compile(r'\\\((?P<m>.*?)\\\)',re.DOTALL)
        display_re2 = re.compile(r'\\\[(?P<m>.*?)\\\]', re.DOTALL)
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
        #if we don't find math we return the tex
        if len(pos) == 0:
            #it couldn't be void because environment
            #parsing never returns void strings
            tokens.append(('text',tex))
            return tokens

        last_tex_index = 0
        for start in sorted(pos.keys()):
            end = pos[start][1].end()
            typ = pos[start][0]
            content = pos[start][1].group('m')
            #the text outside math is extracted and NOT STRIPED
            previous_tex = tex[last_tex_index : start]
            if len(previous_tex)>0:
                #if ok the text is saved
                tokens.append(('text', previous_tex))
            #the last_tex_index is moved forward
            last_tex_index = end
            #the match is saved
            tokens.append((typ, content))
        #the text after last math must be extracted.
        #NOT STRIPED
        last_text = tex[last_tex_index:]
        if len(last_text) > 0:
            tokens.append(('text', last_text))
        return tokens