# -*- coding: utf-8 -*-

import re
from .utils import *


def math_check(mtxt, env=''):
    '''Function that remove and replace some commands from math'''
    #removing inner starred commands
    re_remove_star = re.compile(r'\\begin{(\w+)\*}(.*?)\\end{(\w+)\*}',
                                re.DOTALL)
    for star_tag in re.finditer(re_remove_star, mtxt):
        mtxt = mtxt.replace(star_tag.group(0),'\\begin{'+star_tag.group(1)+'}'+\
            star_tag.group(2)+'\end{'+ star_tag.group(3)+'}')
    #replacing split with align
    mtxt = mtxt.replace("split", "align")
    #removing \boxed command
    mtxt = remove_command_greedy(mtxt, 'boxed',False)
    #removing \ensuremath from macros
    mtxt = remove_command_greedy(mtxt, 'ensuremath', False)
    #removing tiny command
    mtxt = remove_command_greedy(mtxt, 'tiny',False)
    mtxt = remove_command_greedy(mtxt, 'scriptsize')
    #replace hspace with \quad
    mtxt = replace_command_greedy(mtxt, 'hspace', 'quad', True)
    mtxt = replace_command_greedy(mtxt, 'underbar', 'underline', False)
    #replacing bb and bbm with boldmath
    mtxt = replace_command_greedy(mtxt, 'bm', 'mathbf', False)
    mtxt = replace_command_greedy(mtxt, 'bbm', 'mathbf', False)
    mtxt = replace_command_greedy(mtxt, 'mathscr', 'mathcal', False)
    #replace intertext with mbox
    mtxt = replace_command_greedy(mtxt, 'intertext', 'mbox', False)
    #symbols
    mtxt = mtxt.replace('\\abs', '|')
    mtxt = mtxt.replace('\\lvert', '|')
    mtxt = mtxt.replace('\\rvert', '|')
    mtxt = replace_command_greedy(mtxt, 'modul', '', False,
                                  '|', '|',rm_slash=False)
    #removing \nonumber command
    mtxt = mtxt.replace('\\nonumber', '')
    mtxt = mtxt.replace('\\notag', '')
    #dag to dagger
    mtxt = replace_command_no_options(mtxt,'dag', 'dagger')
    mtxt = replace_command_no_options(mtxt,'fint', 'int')
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
    #environment specific changes
    if env == 'empheq':
        mtxt = re.sub(r'\[box=(.*?)\]', '', mtxt, re.DOTALL)

    return mtxt
