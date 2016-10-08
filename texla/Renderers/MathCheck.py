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
    mtxt = remove_command_greedy(mtxt, 'mathsrc', False)
    #removing tiny command
    mtxt = remove_command_greedy(mtxt, 'tiny',False)
    mtxt = remove_command_greedy(mtxt, 'scriptsize')
    #replace hspace with \quad
    mtxt = replace_command_greedy(mtxt, 'hspace', 'quad', True)
    mtxt = replace_command_greedy(mtxt, 'underbar', 'underline', False)
    #replacing bb and bbm with boldmath
    mtxt = replace_command_greedy(mtxt, 'bm', 'mathbf', False)
    mtxt = replace_command_greedy(mtxt, 'bbm', 'mathbf', False)
    #replace intertext with mbox
    mtxt = replace_command_greedy(mtxt, 'intertext', 'mbox', False)
    #symbols
    mtxt = mtxt.replace('\\abs', '|')
    mtxt = mtxt.replace('\\lvert', '|')
    mtxt = mtxt.replace('\\rvert', '|')
    mtxt = mtxt.replace('\\coloneq', ':=')
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

    #Michela Montrasio specific edits
    #greek letters abbreviations
    mtxt = replace_command_no_options(mtxt, '\\a', '\\alpha')
    mtxt = replace_command_no_options(mtxt, '\\b', '\\beta')
    mtxt = replace_command_no_options(mtxt, '\\ga', '\\gamma')
    mtxt = replace_command_no_options(mtxt, '\\d', '\\delta')
    mtxt = replace_command_no_options(mtxt, '\\eps', '\\epsilon')
    mtxt = replace_command_no_options(mtxt, '\\l', '\\lambda')
    mtxt = replace_command_no_options(mtxt, '\\t', '\\theta')
    mtxt = replace_command_no_options(mtxt, '\\s', '\\sigma')
    #number sets
    mtxt = replace_command_no_options(mtxt, '\\N', '\\mathbb{N}')
    mtxt = replace_command_no_options(mtxt, '\\Z', '\\mathbb{Z}')
    mtxt = replace_command_no_options(mtxt, '\\Q', '\\mathbb{Q}')
    mtxt = replace_command_no_options(mtxt, '\\R', '\\mathbb{R}')
    mtxt = replace_command_no_options(mtxt, '\\C', '\\mathbb{C}')
    #generic
    mtxt = replace_command_no_options(mtxt, '\\+', '+ \\dots +')
    mtxt = replace_command_no_options(mtxt, '\\from', '\\colon')
    mtxt = replace_command_no_options(mtxt, '\\ssm', '\\smallsetminus')
    mtxt = replace_command_no_options(mtxt, '\\implies', '\\longrightarrow')
    mtxt = replace_command_no_options(mtxt, '\\v', '\\overrightarrow')

    #To Do List: understand how to treat this stuff
    #\renewcommand{\Re}{\mathop{Re}}
    #\DeclareMathOperator{\spam}{spam}
    #\renewcommand{\Im}{\mathop{Im}}
    #\newcommand{\floor}[1]{\left\lfloor #1 \right\rfloor}
    #\newcommand{\pint}[1]{\mathaccent23{#1}}
    #\newenvironment{sistema}%{\left \lbrace \begin{array}{@{}l@{}}}%{\end{array}\right.}


    return mtxt
