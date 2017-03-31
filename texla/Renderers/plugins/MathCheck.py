# -*- coding: utf-8 -*-
import re
from ..utils import *
import logging

def math_check(block):
    logging.debug("Plugin MathCheck @ checking math")
    #extracting math content to elaborate
    mtxt = block.attributes["content"]
    '''Function that remove and replace some commands from math'''
    #removing inner starred commands
    re_remove_star = re.compile(r'\\begin{(\w+)\*}(.*?)\\end{(\w+)\*}',
                                re.DOTALL)
    for star_tag in re.finditer(re_remove_star, mtxt):
        mtxt = mtxt.replace(star_tag.group(0),'\\begin{'+star_tag.group(1)+'}'+\
            star_tag.group(2)+'\end{'+ star_tag.group(3)+'}')
    #replacing split with align
    mtxt = mtxt.replace("split", "align")
    #removing \par inserted by the preparser
    mtxt = remove_command_no_options(mtxt, 'par')
    #removing \boxed command
    mtxt = remove_command_greedy(mtxt, 'boxed',False)
    #removing \ensuremath from macros
    mtxt = remove_command_greedy(mtxt, 'ensuremath', False)
    mtxt = remove_command_greedy(mtxt, 'mathscr', False)
    #removing tiny command
    mtxt = remove_command_greedy(mtxt, 'tiny',False)
    mtxt = remove_command_greedy(mtxt, 'scriptsize')
    #replace hspace with \quad
    mtxt = replace_command_greedy(mtxt, 'hspace', 'quad', True)
    mtxt = replace_command_greedy(mtxt, 'underbar', 'underline', False)
    #replacing bb and bbm with boldmath
    mtxt = replace_command_greedy(mtxt, 'bm', 'mathbf', False)
    mtxt = replace_command_greedy(mtxt, 'bbm', 'mathbf', False)
    #symbols
    mtxt = mtxt.replace('\\abs', '|')
    mtxt = mtxt.replace('\\lvert', '|')
    mtxt = mtxt.replace('\\rvert', '|')
    mtxt = mtxt.replace("\\middle|", '|')
    mtxt = mtxt.replace('\\coloneq', ':=')
    mtxt = replace_command_greedy(mtxt, 'modul', '', False,
                                  '|', '|',rm_slash=False)
    #removing \nonumber command
    mtxt = mtxt.replace('\\nonumber', '')
    mtxt = mtxt.replace('\\notag', '')
    #dag to dagger
    mtxt = replace_command_no_options(mtxt,'dag', 'dagger')
    mtxt = replace_command_no_options(mtxt,'fint', 'int')
    mtxt = replace_command_no_options(mtxt,'dashrightarrow', 'rightarrow')
    #replacing spacing commands
    mtxt = mtxt.replace('\\:', '\\,')
    #removing rule command
    rule_match = re.search(r'\\rule\s*(\[(.*?)\])?(\s*(\{(.*?)\}))*', mtxt)
    if rule_match:
        mtxt = mtxt.replace(rule_match.group(0), '')
    #removing makebox[]{} command
    mtxt = re.sub(r'\\makebox\s*(\[(.*?)\])*\s?\{(.*?)\}', '', mtxt)
    #removing tag command
    mtxt = remove_command_greedy(mtxt, 'tag', True)
    #apostrophe in math
    mtxt = mtxt.replace('”', "''")
    mtxt = mtxt.replace('"', "''")
    mtxt = mtxt.replace('``', "''")
    mtxt = mtxt.replace('`', "'")
    #remove newline characters in math
    mtxt = mtxt.replace('\n', '')
    #saving content
    block.attributes["content"] = mtxt

plugin_render_hooks = {
    'displaymath': {"pre": math_check},
    'inlinemath': {"pre": math_check},
    'ensuremath': {"pre": math_check},
    'equation': {"pre": math_check},
    'eqnarray': {"pre": math_check},
    'multline': {"pre": math_check},
    'align': {"pre": math_check},
    'alignat': {"pre": math_check},
    'gather': {"pre": math_check}
}
