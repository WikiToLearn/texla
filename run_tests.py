import tests
import Blocks
from Blocks import CommandParser
from Blocks import utility
import unittest

class CommandParserTest(unittest.TestCase):
	def test_grammar_complete(self):
		a = '[option]{text}other text'
		grammar = [('opt','[',']'),('content','{','}')]
		self.assertEqual(CommandParser.parse_command_options(a, grammar),
			{'opt':'option','content':'text'})
	
	def test_grammar_command_near_command(self):
		a = '[option]{text}\cmd{other text}'
		grammar = [('opt','[',']'),('content','{','}')]
		self.assertEqual(CommandParser.parse_command_options(a,grammar),
			{'opt':'option','content':'text'})

	def test_grammar_blank_left(self):
		a = '{text} other text'
		grammar = [('opt','[',']'),('content','{','}')]
		self.assertEqual(CommandParser.parse_command_options(a,grammar),
			{'opt':None,'content':'text'})

	def test_grammar_blank_right(self):
		a = '[option] other text'
		grammar = [('opt','[',']'),('content','{','}')]
		self.assertEqual(CommandParser.parse_command_options(a, grammar),
			{'opt':'option','content':None})

	def test_grammar_blank_middle(self):
		a = '[option1][option2] other text'
		grammar = [('opt1','[',']'),('content','{','}'),
			('opt2','[',']')]
		self.assertEqual(CommandParser.parse_command_options(a, grammar),
			{'opt1':'option1','content':None,
			 'opt2':'option2'})

	def test_grammar_blank_same(self):
		a = '[option1][option2]	other text'
		grammar = [('opt1','[',']'),('opt2','[',']'),
			('opt3','[',']')]
		self.assertEqual(CommandParser.parse_command_options(a, grammar),
			{'opt1':'option1','opt2':'option2',
			 'opt3':None})

	def test_get_parenthesis_nested(self):
		a = '[a][b]{abc\command{}[]}[d]{boh[]} tests'
		self.assertEqual(CommandParser.get_parenthesis(a)[:-1], 
			[('[','a',']'),('[','b',']'),('{','abc\command{}[]','}'),
			('[','d',']'),('{','boh[]','}')]) 
		self.assertEqual(CommandParser.get_parenthesis(a)[-1:],
			[('out',' tests','')])

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
			('[boh]{test{test}}[{boh}a]', ' left tex'))



class UtilityTest(unittest.TestCase):
	def test_get_environment_content(self):
		a = '\\begin{A} test \\begin{A}\nt\n\\end{A}'+\
			'test\ntest\n\\end{A} other test'
		self.assertEqual(utility.get_environment_content(a,'A'),
			' test \\begin{A}\nt\n\\end{A}test\ntest\n')

	def test_get_environment_content_left(self):
		a = 'test \\begin{A} test \\begin{A}\nt\n\\end{A}'+\
			'test\ntest\n\\end{A} other test'
		self.assertEqual(utility.get_environment_content(a,'A'),
			' test \\begin{A}\nt\n\\end{A}test\ntest\n')

	def test_get_environment(self):
		a = 'test \\begin{A} test \\begin{A}\nt\n\\end{A}'+\
			'test\ntest\n\\end{A} other test'
		r = utility.get_environment(a,'A')
		s = r[0]
		e = r[1]
		c = r[2]
		self.assertEqual(a[s:e],'\\begin{A} test \\begin{A}\nt\n\\end{A}'+\
			'test\ntest\n\\end{A}')




if __name__ == '__main__':
    unittest.main()