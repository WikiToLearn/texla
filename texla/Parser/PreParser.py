from .Blocks import TheoremBlocks
from .Blocks.Utilities import *
from collections import deque
import logging
import re
import os

data = {}


def preparse(tex, input_path):
    '''
    Entrypoint for preparsing of tex
    '''
    tex = check_doc_integrity(tex)
    tex = remove_comments(tex)
    tex = preparse_input(tex, input_path)
    tex = parse_macros(tex)
    tex = preparse_theorems(tex)
    tex = preparse_par(tex)
    data = preparse_header(tex)
    o = open('preparsed', 'w')
    o.write(tex)
    return (tex, data)

def check_doc_integrity(tex):
    '''checking if the source has \begin{document}'''
    if not ("\\begin{document}" in tex):
        tex = "\\begin{document}"+tex+ "\\end{document}"
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
    tex_to_parse = tex[:]
    for match in new_re.finditer(tex):
        #first we get the options
        opt_tex = CommandParser.get_command_options(tex[match.end():])
        macro = MacroParser.Macro.parse_macro(opt_tex[0])
        macros[macro.name] = macro
        log[macro.name] = 0
        tex_to_parse = tex_to_parse.replace(
            tex[match.start():match.end() + opt_tex[2]], '')
    #now we can search for occurrence of the macro,
    #get the options, and replace the tex
    macros_found = 0
    #we reiterate the process until no macros are found.
    #This is useful for macros using other macros.
    while True:
        for m in macros:
            logging.debug("preparsing MACRO: %s", m)
            #the macro name is \\name, but it's not
            #raw: we have to add a \\ in front of it.
            #we have to create the string for regex
            #to fix the special characters problem
            m_r = ''.join(['['+x+']' for x in m[1:]])
            cmd_re = re.compile(r'\\' + m_r + r'(?![a-zA-Z])')

            #lists for positions and replacements
            pos = []
            replaces = []
            #first of all we get all the occurrence
            #of a macro and its replacement tex.
            for cmd_ma in cmd_re.finditer(tex_to_parse):
                log[m] += 1
                macros_found += 1
                #we get command complete tex
                cmd_tex = CommandParser.get_command_options(tex_to_parse[
                    cmd_ma.end():])
                #cmd_tex contains also the index of the star  of
                #tex after the macro. We need it later.
                #we get parenthesis
                parenthesis = CommandParser.get_parenthesis(cmd_tex[0])
                if parenthesis[0][0] == '[':
                    param_default = parenthesis[0][1]
                    parenthesis.pop(0)
                else:
                    param_default = None
                params = [parenthesis[i][1]
                          for i in range(len(parenthesis) - 1)]
                #asking the tex to the macro
                replace_tex = macros[m].get_tex(params, param_default)
                #saving data
                replaces.append(replace_tex)
                pos+= [cmd_ma.start(), cmd_ma.end()+cmd_tex[2]]

            #now that we have all macros we can replace them
            if (len(pos) ==0):
                continue
            preparsed_result = [tex_to_parse[:pos[0]]]
            repl_queu = deque(replaces)
            for x in range(1, len(pos)-1, 2):
                preparsed_result.append(repl_queu.popleft())
                preparsed_result.append(tex_to_parse[pos[x]:pos[x+1]])
            #we have to add the last piece
            preparsed_result.append(repl_queu.popleft())
            preparsed_result.append(tex_to_parse[pos[len(pos)-1]:])
            preparsed_tex = ''.join(preparsed_result)
            #for the next macro we have to reset tex_to_parse
            tex_to_parse = preparsed_tex

        #at the end of the all the macros we check if
        #we have found something
        if macros_found > 0:
            macros_found = 0
            #the cycle continues
        else:
            break
    #logging
    for m in log:
        logging.info('PREPARSER @ macro: %s, %s occurrences', m, log[m])
    return tex_to_parse


def remove_comments(tex):
    '''
    This function removes comments from the tex.
    '''
    print(type(tex))
    com_re = re.compile(r'(?<!\\)(%.*)\n')
    final_tex = tex
    for match in com_re.finditer(tex):
        final_tex = final_tex.replace(match.group(1), '')
    return final_tex


def preparse_theorems(tex):
    '''Function that searches \newtheorems command in tex
    source to find the theorems environments used.
    It memorizes them and it normalize them with
    our theorem env.
    '''
    th_dict = {}
    p = re.compile(r'\\newtheorem(?P<star>[*]?)')
    for match in p.finditer(tex):
        t = tex[match.end():]
        data = CommandParser.parse_options(
            t, [('th_type', '{', '}'), ('counter', '[', ']'),
                ('definition', '{', '}'), ('numberby', '[', ']')])
        if match.group('star') != "":
            data[0]['star'] = True
        else:
            data[0]['star'] = False
        the = TheoremBlocks.Theorem(**data[0])
        logging.info('PREPARSER @ theorem: %s', the.th_type)
        th_dict[the.th_type] = the
    #now we search for every theorem \beging{th_id} and \end{th_id}
    #and we substitue them with \begin{theorem}{th_id} and \begin{theorem}
    #to use out theorem environment
    for key in th_dict:
        tag_open = '\\begin{' + key + '}'
        new_tag_open = '\\begin{theorem}{' + key + '}'
        tex = tex.replace(tag_open, new_tag_open)
        tag_close = '\\end{' + key + '}'
        new_tag_close = '\\end{theorem}'
        tex = tex.replace(tag_close, new_tag_close)
    #parsed theorems are saved in TheoremBlocks moduile
    TheoremBlocks.parsed_theorems = th_dict
    return tex


def preparse_header(tex):
    '''Function that searches title, date, author in preamble of the tex
    '''
    headerBlock = {}
    headerBlock['title'] = ''
    headerBlock['date'] = ''
    headerBlock['author'] = ''
    mat = re.search(r'\\title{(.*?)}', tex)
    if mat:
        headerBlock['title'] = mat.group(1)
    mat = re.search(r'\\date{(.*?)}', tex)
    if mat:
        headerBlock['date'] = mat.group(1)
    mat = re.search(r'\\author{(.*?)}', tex)
    if mat:
        headerBlock['author'] = mat.group(1)
    logging.info('PREPARSER @ preparse_header ')
    logging.debug('\ntitle: %s\ndate: '\
            '%s\nauthor: %s', headerBlock['title'], headerBlock['date'],
            headerBlock['author'])
    return headerBlock

def preparse_par(tex):
    '''This function replace \n\n with a \\par to
    show that there's a change of par, understendable by the parser.
    It replaces even occurrences of \n\n'''
    return re.sub(r'(\n\n)+','\\par ',tex)

def preparse_input(tex,input_path):
    ''' This function replace \input{} commands
    with the content of the files.  '''
    base_path = os.path.dirname(input_path)
    print(base_path)
    r = re.compile(r'\\input{(.*?)}')
    inputs_found = 0
    result_tex = tex
    while(True):
        for m in r.finditer(tex):
            name = m.group(1) + '.tex'
            print(m.groups())
            #reading file
            file_name = base_path + "/"+ name
            file_tex = open(file_name, 'r').read()
            result_tex = result_tex.replace(
                        m.group(0), file_tex)
            inputs_found+=1
        if (inputs_found>0):
            tex = result_tex
            inputs_found = 0
        else:
            break
    #now include
    r = re.compile(r'\\include{(.*?)}')
    inputs_found = 0
    #resetting tex
    tex = result_tex
    while(True):
        for m in r.finditer(tex):
            name = m.group(1) + '.tex'
            #reading file
            file_name =os.getcwd()+ '/'+\
                        base_path + "/"+ name
            file_tex = open(file_name, 'r').read()
            result_tex = result_tex.replace(
                        m.group(0), file_tex)
            inputs_found+=1
        if (inputs_found>0):
            tex = result_tex
            inputs_found = 0
        else:
            break
    return result_tex
