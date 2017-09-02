import re
import logging
from . import PreParser
from . import Blocks
from .TreeExplorer import TreeExplorer
from .Utilities import *
from .Blocks.DocumentBlock import DocumentBlock
from ..Exceptions.TexlaExceptions import *

'''Commands that changes directly the subsequent letter'''
letters_commands = ("'","`",'"','~','^','=','.')
special_characters = ('%','&','$','{','}','#','_',' ', '\n')

class Parser:

    def __init__(self, configs):
        self.configs = configs
        self.doc_data = {}
        self.root_block = None
        self.tree_explorer = None

    def parse(self,tex):
        """Entry point for parsing.
        The DocumentBlock is created and all the
        parse chain is started from parse_sections.
        The function returns the root_block,
        which contains all the parsed tree blocks."""
        #preparsing
        tex, doc_data = PreParser.preparse(tex, self.configs['input_path'])
        self.doc_data = doc_data
        logging.info('\033[0;34m############### STARTING PARSING ###############\033[0m')
        #Getting content of document
        r_doc = re.compile(r'\\begin(?P<options>\[.*?\])?{document}'+
                           r'(?P<content>.*?)\\end{document}', re.DOTALL)
        m_doc = r_doc.search(tex)
        #getting content
        content = m_doc.group("content")
        logging.debug('Parser @ got content of Document')
        #creating root block
        self.root_block = DocumentBlock(self.doc_data['title'],{})
        #creating the TreeExplorer
        self.tree_explorer = TreeExplorer(self.root_block)
        #beginning of parsing: creation of root block
        options = {} #for now we don't have options
        blocks = self.parse_sections(content, -1,
                        self.root_block,options)
        self.root_block.add_children_blocks(blocks)
        #updating the tree_explorer
        self.tree_explorer.update_blocks_register()
        return self.tree_explorer


    def parse_sections(self, tex, level, parent_block, options):
        """
        This parser function search for sections splitting inside tex.
        The level of sections searched is indicated by sec_level option.
        The function calls the parser_hooks of every section block.
        When all sections levels are searched the control
        pass to parse_instructions().
        It returns a list of blocks parsed as tuples.
        """
        try:
            pblocks = []
            #check if the level is greater than subparagraph
            if (level+1) < (len(utility.section_level)-1):
                #getting level key from utility to create regex
                level_key = utility.section_level[level+1]
                sec_re = re.compile(r'\\'+ level_key + r'(?![a-zA-Z])')
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
                    if tok.startswith('*'):
                        star = True
                        tok = tok[1:].strip()
                    else:
                        star = False
                        tok = tok.strip()
                    #we insert the level in the options
                    sec_params = { 'sec_level' : (level +1),
                                'level_key' : level_key,
                                'star' : star}
                    #the tuple with the result is saved
                    pblocks.append(self.call_parser_hook(level_key,
                            'env', tok, parent_block, sec_params))
                    logging.debug('Block @ %s%s',
                        "\t"*pblocks[-1].tree_depth,
                        str(pblocks[-1]))
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
        except ParserError as err:
            raise
        except:
            raise ParserError(tex, parent_block, "Error in parse_sections")


    def parse_instructions(self, tex, parent_block, options):
        """This function is the MAIN ENTRY POINT for parsing.
        It scan the tex from left to right. It searches for
        \\ or $. When an instruction is found (a pattern starting
        with \\ or $), the right parser function is called.
        These functions take care to parse the command,
        create the block calling parser_hooks, and to return
        the block and the tex left to parse. Then the remaining
        tex starts a new cycle in parse_instructions() recursively.
        It returnes a list of parsed blocks.

        The categories of instrucions parsed are:
        -math: starts with $, $$ or \[ \(
        -environments: (start with \begin)
        -letters commands: they are special commands
            listed in letters_commands. They are
            parsed separately
        -normal commands: like \cmd{text}
        """
        #printing the current tex for debug
        #logging.debug('CURRENT-TEX: ' + tex[:40])
        #list of blocks parsed
        pblocks = []
        #checking if tex is void
        if len(tex) == 0:
            return pblocks
        #searching for comands \cmd, envs \begin or math
        symb = {}
        left_tex = ''
        slash = tex.find('\\')
        dollar = tex.find('$')
        graph = tex.find('{')
        if slash == -1 and dollar == -1 and graph==-1:
            #we check if the string is only space or \n
            if len(tex.strip()):
                #it's plain text
                pblocks.append(self.parse_plain_text(tex,
                        parent_block))
            return pblocks
        #searching the first symbol
        if slash != -1:
            symb[slash] = 'slash'
        if dollar != -1:
            symb[dollar] = 'dollar'
        if graph != -1:
            symb[graph] = 'group'
        #getting the first occurence
        first_index = sorted(symb)[0]
        first_symb = symb[first_index]
        #creating block text with before_tex
        before_tex = tex[:first_index]
        #tex to parse
        tex_tp = tex[first_index:]
        #creating a plain text block
        if len(before_tex.strip()):
            pblocks.append(self.parse_plain_text(before_tex,
                    parent_block))
        #what's the first token: slash, dollar, group
        if first_symb == 'slash':
            #we check if it's a math command like \[ or \(
            if tex_tp[1] in ('[','('):
                block, left_tex = self.parse_math(
                    tex_tp, parent_block, options)
            #now we check if it's an environment
            elif tex_tp[1:6] == 'begin':
                block, left_tex = self.parse_enviroment(
                    tex_tp, parent_block, options)
            #we check if we have letters commands
            elif tex_tp[1] in letters_commands:
                block, left_tex = self.parse_letter_command(
                    tex_tp, parent_block, options)
            #we check if we have special characters
            elif tex_tp[1] in special_characters:
                block, left_tex = self.parse_special_character(
                    tex_tp, parent_block, options)
            else:
                #finally we have a normal command
                block, left_tex = self.parse_command(
                    tex_tp, parent_block, options)
            #block saved
            pblocks.append(block)
        elif first_symb == 'dollar':
            #we have to parse math
            block, left_tex = self.parse_math(tex_tp, parent_block,options)
            pblocks.append(block)
        elif first_symb == 'group':
            #we have a group {...} syntax
            block, left_tex = self.parse_commands_group(
                    tex_tp, parent_block, options)
            pblocks.append(block)
        #left_tex is parsed with another cycle
        pblocks += self.parse_instructions(
                left_tex, parent_block, options)
        #all the blocks parsed are returned
        return pblocks


    def parse_enviroment(self, tex, parent_block, options):
        """
        This function handles the parsing of environments.
        It parses the name of the environment and if it's starred.
        Then EnvironmentParser.get_environment() is used to extract
        the complete environment, handling nested envs.
        The content is sent to parser_hook for the specific parsing.
        The parser_hook decides also if the content of the env
        must be parsed recursively.
        A new block is created and returned with the tex
        remained to parse.
        """
        try:
            #we search for the first enviroment
            re_env1 = re.compile(r'\\begin(?: *)\{(?: *)(?P<env>\w*?)'+\
                                r'(?P<star>[*]?)(?: *)\}')
            match = re_env1.match(tex)
            if not match is None:
                env = match.group('env')
                star = True if match.group('star')!='' else False
                env_tot = env + '\*' if star else env
                #now we extract the env greedy
                s,e,content = EnvironmentParser.get_environment(
                                                tex,env_tot)
                #the name of catched env is inserted in params
                #with the star param
                env_params = {'env':env, 'star':star}
                #we can call the parser hooks.
                #N.B.: the tex passed to parser hook is the CONTENT STRIPPED
                #of the environment, without \begin{} and \end{} part.
                #The strip is necessary to parse possible options.
                block = self.call_parser_hook(env,'env',
                        content.strip(), parent_block, env_params)
                logging.debug('Block @ %s%s',
                        "\t"*block.tree_depth,
                        str(block))
                #we return the block and left_tex
                return (block, tex[e:])
            else:
                #it's an error
                logging.error('PARSER.parse_enviroment @ env NOT FOUND')
        except ParserError:
            raise
        except:
            raise ParserError(tex, parent_block, "Error in parse_enviroment")


    def parse_math(self, tex, parent_block, options):
        """
        This function handles the parsing of math commands:
        $..$, $$..$$, \[..\], \(..\). The matched math
        is inserted in "display_math" or "inline_math" block.
        The function returnes the block and left_tex.
        """
        try:
            #firt we have to check the double dollar
            if tex.startswith("$$"):
                i = tex.find("$$", 2)
                content = tex[2:i]
                left_tex = tex[i+2:]
                env = "displaymath"
            elif tex.startswith("$"):
                i = tex.find("$", 1)
                content = tex[1:i]
                left_tex = tex[i+1:]
                env = "inlinemath"
            elif tex.startswith("\\["):
                i = tex.find("\\]", 2)
                content = tex[2:i]
                left_tex = tex[i+2:]
                env = "displaymath"
            elif tex.startswith("\\("):
                i = tex.find("\\)", 2)
                content = tex[2:i]
                left_tex = tex[i+2:]
                env = "inlinemath"
            params = {'env': env}
            block = self.call_parser_hook(env, 'env',
                    content, parent_block, params)
            logging.debug('Block @ %s%s',
                        "\t"*block.tree_depth,
                        str(block))
            return (block, left_tex)
        except ParserError:
            raise
        except:
            raise ParserError(tex, parent_block, "Error in parse_math")


    def parse_command(self, tex, parent_block, options):
        """
        This function handles the parsing of normal
        commands. It catches the command's name and if it's
        starred. Removed the \cmd part, the tex is passed
        to the right parser_hook that manages the real
        parsing of commands options. The parser_hook decides
        also if the content of the command must be parsed
        recursively.
        It returns the block and the left tex that must
        be parsed by another cycle of parse_instructions()
        """
        try:
            #regex to catch commands
            re_cmd = re.compile(r"\\(?:(?P<cmd>[a-zA-Z]+)"+\
                                r"(?P<star>[*]?)|(?P<n>\\))", re.DOTALL)
            match = re_cmd.match(tex)
            if not match is None:
                #managing match.
                #checking if the part of the match with the regular
                #command is present--> math.group != None!!!
                if match.group('cmd') != None:
                    matched_cmd = match.group('cmd')
                    star = True if match.group('star')!='' else False
                    #we insert the matched options in the dict for hooks
                    params = {'cmd':matched_cmd, 'star':star}
                    #the text passed to hooks is STRIPPED to remove
                    #useless spaces.
                    #N.B the matched part is not sent to hook
                    tex_to_parse = tex[match.end():].strip()
                    #the matched command is parsed by the parser_hook
                    #and the remaining tex is returned as the second element of
                    #a list.  The first element is the parsed Block.
                    block, left_tex = self.call_parser_hook(matched_cmd,
                            'cmd', tex_to_parse, parent_block,params)
                    logging.debug('Block @ %s%s',
                        "\t"*block.tree_depth,
                        str(block))
                else:
                    #we have a \\ command
                    matched_cmd = '\\'
                    tex_to_parse = tex[match.end():].strip()
                    #we insert the matched options in the dict for hooks
                    params = {'cmd':'\\', 'star':False}
                    #check if we have \\*
                    if tex_to_parse.startswith('*'):
                        params['star'] = True
                        tex_to_parse = tex_to_parse[1:]
                    #parser_hook call
                    block, left_tex = self.call_parser_hook(matched_cmd,
                            'cmd', tex_to_parse, parent_block,params)
                    logging.debug('Block @ %s%s',
                        "\t"*block.tree_depth,
                        str(block))
                return (block, left_tex)
            else:
                #it's an error
                logging.error('PARSER.parse_command @ command NOT FOUND: {}'.
                              format(tex[0:10]))
                raise ParserError(tex, parent_block, "command NOT FOUND in parse_command")
        except ParserError:
            raise
        except:
            raise ParserError(tex, parent_block, "Error in parse_command")


    def parse_commands_group(self, tex, parent_block, options):
        """
        This function handles the group of commands created
        with the syntax {...}. It's used for the formatting
        commands.
        """
        block, left_tex = self.call_parser_hook(
            'commands_group', 'env', tex, parent_block,
            {'env':'commands_group'})
        return (block, left_tex)

    def parse_letter_command(self, tex, parent_block,options):
        """'
        This function handles special commands for accented
        or modified letters.
        They are special commands because they don't need a {}
        and they act directly on the next letter.
        Examples:
        \'a: accented letter
        \`a: grave accent
        \~a \=a \^a other changes on the letter

        The function parse that commands and call
        parser_hook as the normal parse_command() function.
        Althought, the letter influenced by the command is
        inserted in a {} so that special command could
        be treated like normal commands with hooks.
        It returns the block and the left tex to parse.
        """
        #first of all we get the command
        cmd = tex[1]
        params = {'cmd':cmd, 'star':False}
        #then it is a letter command
        #check if the letter is inside a {}
        r = re.compile(r'\\' + cmd + r'\s*\{(.*?)\}')
        match = r.match(tex)
        if match != None:
            tex_to_parse = tex[2:].strip()
            block, left_tex =  self.call_parser_hook(cmd,
                    'cmd', tex_to_parse, parent_block,params)
        else:
            #we have to catch the next letter
            re_letter = re.compile(r'\\' + cmd + r'\s*(?P<letter>\w)')
            letter_m = re_letter.match(tex)
            letter = letter_m.group('letter')
            #adding parenthesis to standardize parser_hook
            tex_to_parse = '{'+letter + '}'+ \
                    tex[letter_m.end():]
            block, left_tex =  self.call_parser_hook(cmd,
                    'cmd', tex_to_parse, parent_block, params)
        logging.debug('Block @ %s%s', "\t"*block.tree_depth,
                    str(block))
        return (block, left_tex)

    def parse_special_character(self, tex, parent_block,options):
        """
        This function parse special commands like \% or \&.
        The mechanism is the same ad special_commands, but options
        are not searched.
        """
        cmd = tex[1]
        if cmd in [' ','\n']:
            #we change the name of the command
            cmd = "mandatory_space"
        params = {'cmd':cmd, 'star':False}
        block, left_tex =  self.call_parser_hook(cmd,
                'cmd', tex[2:], parent_block, params)
        logging.debug('Block @ %s%s', "\t"*block.tree_depth,
                    str(block))
        return (block, left_tex)


    def parse_plain_text(self, tex, parent_block):
        """
        This function create the block for plain text.
        It doesn't return any left tex.
        """
        params = {'env':'text'}
        block = self.call_parser_hook('text','env',
                tex, parent_block,params)
        logging.debug('Block @ %s%s',
                    "\t"*block.tree_depth,
                    str(block))
        return block


    def call_parser_hook(self, hook, type, tex, parent_block, params={}):
        """
        This function checks if the required parser_hook
        is avaiable, if not it calls th default hook.
        The function ask for type of call (env or cmd)
        to be able of asking the right default hooks,
        in case the hook in not avaiable.
        Params is a dictionary of options for the parser. It
        usually contains che env or cmd parsed and if it's
        starred.
        It returns directly the output of parser_hook.
        """
        if hook in Blocks.parser_hooks:
            return Blocks.parser_hooks[hook](self, tex,
                    parent_block, params)
        else:
            #default hook is called
            if type == 'cmd':
                return Blocks.parser_hooks['default_cmd'](
                    self, tex, parent_block, params)
            elif type == 'env':
                return Blocks.parser_hooks['default_env'](
                    self, tex, parent_block, params)
