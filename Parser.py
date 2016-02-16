import os
import re
import logging
import Blocks
import Blocks.utility as utility  
from Blocks.DocumentBlock import DocumentBlock

class Parser:

    def __init__(self):
        pass


    def parse(self,tex):
        ###TODO:preparsing
        #reading title...
        #reading author...

        #Getting content of document
        r_doc = re.compile(r'\\begin(?P<options>\[.*?\])?{document}(?P<content>.*?)\\end{document}', re.DOTALL)
        m_doc = r_doc.search(tex)
        #getting content
        content = m_doc.group("content")
        options = m_doc.group("options")
        logging.debug('PARSER @ got content of Document')
        #creating root block
        self.root_block = DocumentBlock('',{})
        #beginning of parsing 
        options = {'parse_sections':True,
                   'parse_envs':True,
                   'parse_math':True,
                   'parse_commands':True,
                   'sec_level':-1}
        blocks = self.parser_cycle(content, self.root_block,options)
        return blocks


    def parser_cycle(self, tex, parent_block, options):
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
        #list for result
        parsed_blocks = []
        #first of all we search for sectioning if enables
        if options['parse_sections']:
            logging.debug('PARSER.pcyle.SECTIONS @ options: %s', str(options))
            parsed_blocks+=self.parse_sections(tex, parent_block, options)
        #then we parse environments
        elif options['parse_envs']:
            logging.debug('PARSER.pcyle.ENVIRONMENTS @ options: %s', str(options))
            parsed_blocks+=self.parse_environments(tex, parent_block, options)
        elif options['parse_math']:
            #then we parse maths
            logging.debug('PARSER.pcyle.MATH @ options: %s', str(options))
            parsed_blocks+=self.parse_math(tex, parent_block, options)
        elif options['parse_commands']:
            #finally single command are parserd
            logging.debug('PARSER.pcyle.COMMANDS @ options: %s', str(options))
            parsed_blocks+=self.parse_commands(tex, parent_block, options)
        return parsed_blocks


    def parse_sections(self, tex, parent_block, options):
        '''
        This parser function search for sections splitting inside tex.
        The level of sections searched is indicated by sec_level option.
        The function calls the parser_hooks of every section block.

        It returns a list of blocks parsed as tuples.
        '''
        pblocks = []
        level = options['sec_level']
        #check if the level is greater than subparagraph
        if (level+1) < (len(utility.section_level)-1):
            #getting level key from utility to create regex
            level_key = utility.section_level[level+1]
            sec_re = re.compile(r'\\'+ level_key + \
                r'(?:[*])?(?: *)'+\
                r'(?=[\{\[])')
            #the tex is splitted by the section key
            toks = sec_re.split(tex)
            #the first token is the tex outside sectioning
            #the text is STRIPED to avoid null strings
            outside_sec = toks.pop(0).strip()
            if outside_sec != '':
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
                pblocks.append(self.call_parser_hook(level_key,'env', tok, 
                                 parent_block, sec_options))
                logging.info('PARSER.SECTIONS @ block: %s', str(pblocks[-1]))
        else:
            #if we have searched for all section levels 
            #we continue with environments
            #First we STRIP the tex
            #and check if tex is not void
            new_tex = tex.strip()
            if len(new_tex) > 0:
                new_options = options.copy()
                new_options['parse_sections'] = False
                pblocks+= self.parser_cycle(new_tex,parent_block,new_options)
        #found block are returned to main cycle
        return pblocks      


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
        #now we can further analyze text tokens
        #and elaborate with parser_hooks the math founded
        for e in toks:
            if e[0] == 'text':
                #we make sure that the section and env check is disabled
                #because sectioning and envs are parsed before math
                new_options = options.copy()
                new_options['parse_sections'] = False
                new_options['parse_envs'] = False
                new_options['parse_math'] = False
                pblocks+=self.parser_cycle(e[1], parent_block, new_options)
            else:
                env = e[0]
                #we can call the parser hooks
                poptions = {'env': env}
                pblocks.append(self.call_parser_hook(env,'env', e[1],
                        parent_block, poptions))
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


    def parse_commands(self, tex, parent_block, options):
        ''' 
        This function parse single latex commands. Sectioning, environments
        and math are already parsed. The function finds the first command and 
        call the proper parser_hook. The hook elaborate the command and returns
        the new Block and the tex left to parse. Then the fuction is called 
        recursively.
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
            text = tex[:match.start()].strip()
            if len(text)>0:
                #We have to create a text block
                pblocks.append(self.call_parser_hook('text','cmd',
                        text, parent_block)[0])
                logging.info('PARSER.COMMANDS @ block: %s', str(pblocks[-1]))
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
                    pblocks+=self.parse_commands(tex_left, parent_block, options)
            
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
                    pblocks+=self.parse_commands(tex_left, parent_block, options)
        else:
            #a text block is created
            pblocks.append(self.call_parser_hook('text','cmd', tex, parent_block)[0])
            logging.info('PARSER.COMMANDS @ block: %s', str(pblocks[-1]))
        return pblocks


    def call_parser_hook(self,hook, type, tex, parent_block, options={}):
        '''
        This function check if the required parser_hook is avaiable,
        if not it calls th default hook
        '''
        if hook in Blocks.parser_hooks:
            return Blocks.parser_hooks[hook](self, tex, parent_block, options)
        else:
            #default hook is called
            if type == 'cmd':
                return Blocks.parser_hooks['default_cmd'](self, tex, parent_block, options)
            elif type == 'env':
                return Blocks.parser_hooks['default_env'](self, tex, parent_block, options)


