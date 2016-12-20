import re
import texla.Parser.Blocks
from texla.Parser.Blocks.Utilities import *
import texla.Renderers.utils as ut
import texla.Renderers.plugins.MathCheck as mc
import texla.PageTree.PageTree as pt
import unittest

class CommandParserTest(unittest.TestCase):
    def test_grammar_complete(self):
        a = '[option]{text}other text'
        grammar = [('opt','[',']'),('content','{','}')]
        self.assertEqual(CommandParser.parse_options(a, grammar),
            ({'opt':'option','content':'text'}, 'other text'))

    def test_grammar_command_near_command(self):
        a = '[option]{text}\cmd{other text}'
        grammar = [('opt','[',']'),('content','{','}')]
        self.assertEqual(CommandParser.parse_options(a,grammar),
            ({'opt':'option','content':'text'},'\cmd{other text}'))

    def test_grammar_blank_left(self):
        a = '{text} other text'
        grammar = [('opt','[',']'),('content','{','}')]
        self.assertEqual(CommandParser.parse_options(a,grammar),
            ({'opt':None,'content':'text'},' other text'))

    def test_grammar_blank_right(self):
        a = '[option] other text'
        grammar = [('opt','[',']'),('content','{','}')]
        self.assertEqual(CommandParser.parse_options(a, grammar),
            ({'opt':'option','content':None},' other text'))

    def test_grammar_blank_middle(self):
        a = '[option1][option2] other text'
        grammar = [('opt1','[',']'),('content','{','}'),
            ('opt2','[',']')]
        self.assertEqual(CommandParser.parse_options(a, grammar),
            ({'opt1':'option1','content':None,
            'opt2':'option2'},' other text'))

    def test_grammar_blank_same(self):
        a = '[option1][option2] other text'
        grammar = [('opt1','[',']'),('opt2','[',']'),
            ('opt3','[',']')]
        self.assertEqual(CommandParser.parse_options(a, grammar),
            ({'opt1':'option1','opt2':'option2',
             'opt3':None},' other text'))

    def test_grammar_nooptions(self):
        self.assertEqual(CommandParser.parse_options(' text',[]),
            ({},' text'))

    def test_grammar_envinside(self):
        a =  '{test $x=y$ text \\begin{align*}A'+\
            '\end{align*} text}'
        grammar = [('content','{','}')]
        self.assertEqual(CommandParser.parse_options(a,grammar),
            ({'content':'test $x=y$ text \\begin{align*}A'+\
            '\end{align*} text'},''))

    def test_grammar_get_param_with_env(self):
        a =  '{test $x=y$ text \\begin{align*}A'+\
            '\end{align*} text}'
        grammar = [('content','{','}')]
        self.assertEqual(
            CommandParser.parse_options(a,grammar)[0]['content'],
            'test $x=y$ text \\begin{align*}A'+\
            '\end{align*} text')

    def test_get_parenthesis_nested(self):
        a = '[a][b]{abc\command{}[]}[d]{boh[]} tests'
        self.assertEqual(CommandParser.get_parenthesis(a)[:-1],
            [('[','a',']'),('[','b',']'),('{','abc\command{}[]','}'),
            ('[','d',']'),('{','boh[]','}')])
        self.assertEqual(CommandParser.get_parenthesis(a)[-1:],
            [('out',' tests','')])

    def test_get_parenthesis_env(self):
        a =  '{test $x=y$ text \\begin{align*}A'+\
            '\end{align*} text}'
        self.assertEqual(CommandParser.get_parenthesis(a),
            [('{','test $x=y$ text \\begin{align*}A'+\
            '\end{align*} text','}'),('out','','')])

    def test_get_parenthesis_near_command(self):
        a = '[a][b]{abc\command{}[]}[d]{boh[]}\cmd2{tests}'
        self.assertEqual(CommandParser.get_parenthesis(a)[:-1],
            [('[','a',']'),('[','b',']'),('{','abc\command{}[]','}'),
            ('[','d',']'),('{','boh[]','}')])
        self.assertEqual(CommandParser.get_parenthesis(a)[-1:],
            [('out','\cmd2{tests}','')])


    def test_get_command_greedy(self):
        a = '\command[a][b]{abc\emph{}[]}[d]{boh[]}\cmd2{tests}'
        self.assertEqual(CommandParser.get_command_greedy(a),
            ('command','\command[a][b]{abc\emph{}[]}[d]{boh[]}',
                 '\cmd2{tests}',38))

    def test_get_command_options(self):
        a = '[boh]{test{test}}[{boh}a] left tex'
        self.assertEqual(CommandParser.get_command_options(a),
            ('[boh]{test{test}}[{boh}a]', ' left tex',25))


class UtilityTest(unittest.TestCase):
    def test_get_environment_content(self):
        a = '\\begin{A} test \\begin{A}\nt\n\\end{A}'+\
            'test\ntest\n\\end{A} other test'
        self.assertEqual(EnvironmentParser.get_environment_content(a,'A'),
            ' test \\begin{A}\nt\n\\end{A}test\ntest\n')

    def test_get_environment_content_left(self):
        a = 'test \\begin{A} test \\begin{A}\nt\n\\end{A}'+\
            'test\ntest\n\\end{A} other test'
        self.assertEqual(EnvironmentParser.get_environment_content(a,'A'),
            ' test \\begin{A}\nt\n\\end{A}test\ntest\n')

    def test_get_environment(self):
        a = 'test \\begin{A} test \\begin{A}\nt\n\\end{A}'+\
            'test\ntest\n\\end{A} other test'
        r = EnvironmentParser.get_environment(a,'A')
        s = r[0]
        e = r[1]
        c = r[2]
        self.assertEqual(a[s:e],'\\begin{A} test \\begin{A}\nt\n\\end{A}'+\
            'test\ntest\n\\end{A}')

class RegexTest(unittest.TestCase):
    def test_section_regex(self):
        sec = re.compile(r'\\section' + \
                r'(?:[*])?(?: *)'+\
                r'(?=[\{\[])')
        a = 'text tex \\section* {} text '+\
            '\\section text'
        self.assertEqual(sec.split(a),
            ['text tex ','{} text \\section text'])

    def test_section_regex2(self):
        sec = re.compile(r'\\section' + \
                r'(?:[*])?(?: *)'+\
                r'(?=[\{\[])')
        a = 'text tex \\section* {} text '+\
            '\\section[] text'
        self.assertEqual(sec.split(a),
            ['text tex ','{} text ','[] text'])

class UtilTest(unittest.TestCase):
    def test_remove_command_greedy1(self):
        a = 'tex text \\command[option][option2]{ok \\test{} ok} text'
        result = ut.remove_command_greedy(a, 'command', False)
        self.assertEqual(result, 'tex text ok \\test{} ok text')

    def test_remove_command_greedy2(self):
        a = 'tex text \\command{ok \\test{} ok} text'
        result = ut.remove_command_greedy(a, 'command', True)
        self.assertEqual(result, 'tex text  text')

    def test_remove_command_no_option(self):
        a = 'tex text \\command\\par{} text \\command'
        result = ut.remove_command_no_options(a, 'command')
        self.assertEqual(result, 'tex text \\par{} text ')

    def test_remove_command_greedy_multi(self):
        a = 'tex \\cmd{bo} tex \\cmd{foo} text'
        result = ut.remove_command_greedy(a, 'cmd', False)
        self.assertEqual(result, 'tex bo tex foo text')

    def test_replace_command_greedy1(self):
        a = 'tex text \\command[option]{ok ok} text'
        result = ut.replace_command_greedy(a, 'command','cmd',False)
        self.assertEqual(result,
                'tex text \\cmd{ok ok} text', msg=None)

    def test_replace_command_greedy2(self):
        a = 'tex text \\command[option]{ok ok} text'
        result = ut.replace_command_greedy(a, 'command','cmd',True)
        self.assertEqual(result,
                'tex text \\cmd text', msg=None)

    def test_replace_command_greedy3(self):
        a = 'tex text \\command{ok ok} text'
        result = ut.replace_command_greedy(a, 'command','cmd',False)
        self.assertEqual(result,
                'tex text \\cmd{ok ok} text', msg=None)

    def test_replace_command_greedy_multi(self):
        a = 'tex \\cmd{tex} text \\cmd{ok ok} text'
        result = ut.replace_command_greedy(a, 'cmd','command',False)
        self.assertEqual(result,
                'tex \\command{tex} text \\command{ok ok} text')

    def test_replace_command_no_options(self):
        a = 'tex text \\dag\\int text'
        result = ut.replace_command_no_options(a, 'dag','dagger')
        self.assertEqual(result,
                'tex text \\dagger\\int text', msg=None)

    def test_replace_command_greedy_delim(self):
        a = 'tex text \\modul{10} text'
        result = ut.replace_command_greedy(a, 'modul','',False,
                                           "|","|",rm_slash=True)
        self.assertEqual(result,
                'tex text |10| text', msg=None)

    def test_replace_command_greedy_space(self):
        a = 'tex text \\modul{10}text'
        result = ut.replace_command_greedy(a, 'modul','test',False)
        self.assertEqual(result,
                'tex text \\test{10} text', msg=None)

    def test_get_content_greedy(self):
        a = 'tex text \\command[option]{content} text'
        result = ut.get_content_greedy(a, 'command')
        self.assertEqual(result,"content", msg=None)

class TitleTest(unittest.TestCase):
    def test_title_normalizaton(self):
        title = 'title $math \\frac{1}{2}$'
        result = pt.PageTree.get_normalized_title(title)
        self.assertEqual(result, 'title math frac12')

class MathCheckTest(unittest.TestCase):

    def checkApostrophe(self):
        math = 'u" = x" y'
        result = mc.math_check(math, env='')
        self.assertEqual(result, "u'' = x'' y")


if __name__ == '__main__':
    unittest.main()
