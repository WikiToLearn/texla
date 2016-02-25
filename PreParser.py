import re
import logging
from Blocks import CommandParser
from Blocks import MacroParser
from Blocks import utility


def preparse(tex):
    tex = parse_macros(tex)
    return tex


def parse_macros(tex):
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
        logging.info('MACRO preparsed @ name: %s, %s occurrences',
                    m, log[m])
    return preparsed_tex



