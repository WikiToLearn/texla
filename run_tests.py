import tests
import Blocks
from Blocks import CommandParser
from Blocks import utility
import unittest

class CommandParserTest(unittest.TestCase):
	def test_grammar_complete(self):
		a = '\command[option]{text}other text'
		grammar = [('opt','[',']'),('content','{','}')]
		self.assertEqual(CommandParser.get_command_options(a,'command',grammar),
			{'opt':'option','content':'text'})
	
	def test_grammar_command_near(self):
		a = '\command[option]{text}\cmd{other text}'
		grammar = [('opt','[',']'),('content','{','}')]
		self.assertEqual(CommandParser.get_command_options(a,'command',grammar),
			{'opt':'option','content':'text'})

	def test_grammar_blank_left(self):
		a = '\command{text} other text'
		grammar = [('opt','[',']'),('content','{','}')]
		self.assertEqual(CommandParser.get_command_options(a,'command',grammar),
			{'opt':None,'content':'text'})

	def test_grammar_blank_right(self):
		a = '\command[option] other text'
		grammar = [('opt','[',']'),('content','{','}')]
		self.assertEqual(CommandParser.get_command_options(a,'command',grammar),
			{'opt':'option','content':None})

	def test_grammar_blank_middle(self):
		a = '\command[option1][option2] other text'
		grammar = [('opt1','[',']'),('content','{','}'),
			('opt2','[',']')]
		self.assertEqual(CommandParser.get_command_options(a,'command',grammar),
			{'opt1':'option1','content':None,
			 'opt2':'option2'})

	def test_grammar_blank_same(self):
		a = '\command[option1][option2]	other text'
		grammar = [('opt1','[',']'),('opt2','[',']'),
			('opt3','[',']')]
		self.assertEqual(CommandParser.get_command_options(a,'command',grammar),
			{'opt1':'option1','opt2':'option2',
			 'opt3':None})

	def test_gramma_star(self):
		a = '\command*[option]{text} other text'
		grammar = [('opt','[',']'),('content','{','}')]
		self.assertEqual(CommandParser.get_command_options(a,'command*',grammar),
			{'opt':'option','content':'text'})

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