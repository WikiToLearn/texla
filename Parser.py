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
        options = {} #for now we don't have options
        blocks = self.parse_sections(content, -1, self.root_block,options)
        return blocks


    def parse_sections(self, tex, level, parent_block, options):
        '''
        This parser function search for sections splitting inside tex.
        The level of sections searched is indicated by sec_level option.
        The function calls the parser_hooks of every section block.

        It returns a list of blocks parsed as tuples.
        '''
        pblocks = []
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
                pblocks+=self.parse_sections(outside_sec, 
                        level+1, parent_block, options)
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
            #we continue with instructions
            #First we STRIP the tex and check if tex is not void
            new_tex = tex.strip()
            if len(new_tex) > 0:
                pblocks += self.parse_instructions(new_tex,
                        parent_block, options)
        #found block are returned to main cycle
        return pblocks      


    def parse_instructions(self, tex, parent_block, options):
        print(tex)
        #list of blocks parsed
        pblocks = []
        #checking if tex is void
        if len(tex) == 0:
            print('len0')
            return pblocks
        #searching for comands \cmd, envs \begin or math
        slash = tex.find('\\')
        dollar = tex.find('$')
        left_tex = ''
        if slash == -1 and dollar == -1:
            #it's plain text
            pblocks.append(self.parse_plain_text(tex, 
                    parent_block))
            return pblocks
        #what's the first token: cmd,env or math
        if (slash < dollar and slash!=-1 and slash!=-1) or dollar==-1:
            #text before and to parse
            before_tex = tex[:slash]
            tex_tp = tex[slash:]
            if len(before_tex) > 0:
                #creating a plain text block
                pblocks.append(self.parse_plain_text(before_tex,
                        parent_block))
            #we check if it's a math command like \[ or \(
            if tex_tp[1:2] in ('[','('):
                block, left_tex = self.parse_math(
                    tex_tp, parent_block, options)
                print('LEFT#',left_tex,'#')
            #now we check if it's an environment
            if tex_tp[1:6] == 'begin':
                block, left_tex = self.parse_enviroment(
                    tex_tp, parent_block, options)
            else:
                #finally we have a command
                block, left_tex = self.parse_command(
                    tex_tp, parent_block, options)
            #block saved
            pblocks.append(block)
        else:
            if dollar == -1:
                #it's plain text
                pblocks.append(self.parse_plain_text(tex, 
                    parent_block))
            #test before is plain text. 
            before_tex = tex[:dollar]
            tex_tp = tex[dollar:]
            if len(before_tex) > 0:
                pblocks.append(self.parse_plain_text(
                    before_tex, parent_block))
            #we have to parse math
            block, left_tex = self.parse_math(tex_tp, parent_block,options)
            pblocks.append(block)

        #left_tex is parsed with another cycle
        pblocks += self.parse_instructions(left_tex, parent_block, options)
        return pblocks


    def parse_enviroment(self, tex, parent_block, options):
        #we search for the first enviroment
        re_env1 = re.compile(r'\\begin\{(?: *)(?P<env>\w*?)'+\
                            r'(?P<star>[*]?)(?: *)\}')
        match = re_env1.match(tex)
        if not match == None:
            env = match.group('env')
            star = True if match.group('star')!='' else False
            env_tot = env + '\*' if star else env
            #now we extract the env greedy
            s,e,content = utility.get_environment(tex,env_tot)
            #the name of catched env is inserted in options
            #with the star param
            env_options = {'env':env, 'star':star}
            #we can call the parser hooks.
            #N.B.: the tex passed to parser hook is the CONTENT STRIPPED
            #of the environment, without \begin{} and \end{} part.
            block = self.call_parser_hook(env,'env', 
                    content.lstrip(), parent_block, env_options)
            #we return the block and left_tex
            return (block, tex[e:])
        else:
            #it's an error
            logging.error('PARSER.parse_enviroment @ env NOT FOUND')
            
            

    def parse_math(self, tex, parent_block, options):
        inline_re = re.compile(r'(?<![\$])\$(?P<m>[^$]+)\$(?!\$)', re.DOTALL)
        display_re = re.compile(r'(?<![\$])\$\$(?P<m>[^$]+)\$\$(?!\$)', re.DOTALL)
        inline_re2 = re.compile(r'\\\((?P<m>.*?)\\\)',re.DOTALL)
        display_re2 = re.compile(r'\\\[(?P<m>.*?)\\\]', re.DOTALL)
        #searching for match
        matches = []
        matches.append((inline_re.match(tex),'inline_math'))
        matches.append((display_re.match(tex),'display_math'))
        matches.append((inline_re2.match(tex),'inline_math'))
        matches.append((display_re2.match(tex),'display_math'))
        for m, env in matches:
            if m != None:
                content = m.group('m')
                left_tex = tex[m.end():]
        poptions = {'env': env}
        print('left_tex_math#',left_tex,'#')
        block = self.call_parser_hook(env,'env', 
                content, parent_block, poptions)
        return (block, left_tex)


    def parse_command(self, tex, parent_block, options):
        print(tex)
        re_cmd = re.compile(r"\\(?:(?P<cmd>[a-zA-Z']+)"+\
                    r"(?P<star>[*]?)|(?P<n>\\))", re.DOTALL)
        match = re_cmd.match(tex)
        if match!=None:
            #managing match
            if match.group('cmd') != None:
                matched_cmd = match.group('cmd')
                star = True if match.group('star')!='' else False
                #we insert the matched options in the dict for hooks
                opts = {'cmd':matched_cmd, 'star':star}
                #the text passed to hooks is LEFT-STRIPPED to remove
                #spaces between commands and options.
                #N.B the matched part is not sent to hook
                tex_to_parse = tex[match.end():].lstrip()
                #the matched command is parsed by the parser_hook
                #and the remaining tex is returned as the second element of
                #a list.  The first element is the parsed Block.
                block, left_tex = self.call_parser_hook(matched_cmd,'cmd',
                        tex_to_parse, parent_block,opts)
            else:
                #we have a \\ command
                matched_cmd = '\\'
                tex_to_parse = tex[match.end():].lstrip()
                #we insert the matched options in the dict for hooks
                opts = {'cmd':'\\', 'star':False}
                #check if we have \\*
                if tex_to_parse.startswith('*'):
                    opts['star'] = True
                    tex_to_parse = tex_to_parse[1:]
                #parser_hook call
                block, left_tex = self.call_parser_hook(matched_cmd,'cmd',
                        tex_to_parse, parent_block,opts)
            return (block, left_tex)
        else:
            #it's an error
            logging.error('PARSER.parse_command @ command NOT FOUND')


    def parse_plain_text(self, tex, parent_block):
        poptions = {'env':'text'}
        return self.call_parser_hook('text','env', 
                tex, parent_block,poptions)


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


