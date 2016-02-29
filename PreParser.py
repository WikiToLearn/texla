import re
import logging
from Blocks.Utilities import *
from Blocks import TheoremBlocks


def preparse(tex):
    '''
    Entrypoint for preparsing of tex
    '''
    tex = remove_comments(tex)
    tex = parse_macros(tex)
    tex = preparseTheorems(tex)
    o = open('preparsed','w')
    o.write(tex)
    return tex


def parse_macros(tex):
    '''
    Preparsing of macros:
    \newcommand are searched and macro objects
    created. Then the occurrences of the macro
    are replaced with the tex from the macro.
    '''
    #regex for newcommand
    new_re = re.compile(r'\\newcommand')
    macros = {}
    log = {}
    tex_to_parse = tex
    for match in new_re.finditer(tex):
        #first we get the options
        opt_tex = CommandParser.get_command_options(
            tex[match.end():])
        macro = MacroParser.Macro.parse_macro(opt_tex[0])
        macros[macro.name] = macro
        log[macro.name] = 0
        tex_to_parse = tex_to_parse.replace(tex[match.start():
                match.end()+opt_tex[2]],'')
    #now we can search for occurrence of the macro,
    #get the options, and replace the tex
    preparsed_tex = tex_to_parse
    macros_found = 0
    #we reiterate the process until no macros are found.
    #This is useful for macros using other macros.
    while True:
        for m in macros:
            #the macro name is \\name, but it's not
            #raw: we have to add a \\ in front of it.
            cmd_re = re.compile('\\'+ m+r'(?=[\s\{\[])')
            for cmd_ma in cmd_re.finditer(tex_to_parse):
                log[m]+=1
                macros_found+=1
                #we get command complete tex
                cmd_tex = CommandParser.get_command_options(
                        tex_to_parse[cmd_ma.end():])
                #cmd_tex contains also the index of the end of
                #the command. We need it later.
                #we get parenthesis
                parenthesis = CommandParser.get_parenthesis(
                        cmd_tex[0])
                if parenthesis[0][0] == '[':
                    param_default = parenthesis[0][1]
                    parenthesis.pop(0)
                else:
                    param_default = None
                params = [parenthesis[i][1] for i in range(
                            len(parenthesis)-1)]
                #asking the tex to the macro
                replace_tex = macros[m].get_tex(params, param_default)
                #now we replace the tex
                preparsed_tex = preparsed_tex.replace(
                    tex_to_parse[cmd_ma.start():
                    cmd_ma.end()+cmd_tex[2]], replace_tex)
        #at the end of the cyle we check if a macro was found
        if macros_found > 0:
            tex_to_parse = preparsed_tex
            macros_found = 0
            #the cycle continues
        else:
            break
    #logging
    for m in log:
        logging.info('PREPARSER @ macro: %s, %s occurrences',
                    m, log[m])
    return preparsed_tex


def remove_comments(tex):
    '''
    This function removes comments from the tex.
    '''
    com_re = re.compile(r'(%.*)\n')
    for match in com_re.finditer(tex):
        tex = tex.replace(match.group(1), '')
    return tex

def preparseTheorems(tex):
    '''Function that searches \newtheorems command in tex
    source to find the theorems environments used.
    It memorizes them and it normalize them with
    our theorem env.
    '''
    th_dict = {}
    p = re.compile(r'\\newtheorem(?P<star>[*]?)')
    for match in p.finditer(tex):
        t = tex[match.end():]
        data = CommandParser.parse_options(t,
               [('name','{','}'),('counter','[',']'),
                ('definition','{','}'),('numberby','[',']')])
        if match.group('star') != None:
            data[0]['star'] = True
        else:
            data[0]['star'] = False
        the = TheoremBlocks.Theorem(**data[0])
        logging.info('PREPARSER @ theorem: %s', the.name)
        th_dict[the.name] = the
    #now we search for every theorem \beging{th_id} and \end{th_id}
    #and we substitue them with \begin{theorem}{th_id} and \begin{theorem}
    #to use out theorem environment
    for key in th_dict:
        tag_open = u'\\begin{'+key+'}'
        new_tag_open = u'\\begin{theorem}{'+key+'}'
        tex = tex.replace(tag_open, new_tag_open)
        tag_close = u'\\end{'+key+'}'
        new_tag_close = u'\\end{theorem}'
        tex = tex.replace(tag_close, new_tag_close)
    #parsed theorems are saved in TheoremBlocks moduile
    TheoremBlocks.parsed_theorems = th_dict
    return tex
