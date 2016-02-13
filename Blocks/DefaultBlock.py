'''Default Block'''
from . import utility
from .Block import *

class DefaultBlock(Block):

	@staticmethod
	def parse_env(parser ,tex, parent_block, options):
		#getting the name of env
		if 'env_name' in options:
			env_name = options['env_name']
		else:
			env_name = 'no_env'
		#default block is created
		block = DefaultBlock(tex, env_name, parent_block)
		#We cannot look inside tex, we don't know
		#what to parser.
		#we return the block
		return block

	@staticmethod
	def parse_cmd(parser ,tex, parent_block, options):
		#the command has to be extracted with all the options. 
		match = utility.get_command_greedy(tex)
		#match is (commands_tex, command, left_tex, index for starting_tex)
		#default block is created
		cmd_name = match[1]
		if cmd_name!= '':
			block = DefaultBlock(match[0], cmd_name, parent_block)
		else:
			block = DefaultBlock(match[0], 'no_cmd', parent_block)
		#we return the block and the left tex to parse
		return (block, match[2])

	def __init__(self, tex, block_name, parent_block):
		'''
		Constructor for sections:
		-title: main title
		-index_title: title for table of content
		-numbered: True/False
		-level: sections level
		-parent_block
		'''
		#base constructor for Block. It created the id 
		#nd basic data structures
		super().__init__('default-'+block_name, parent_block)
		self.tex = tex
		#the tex is added also as attribute
		self.attributes['tex'] = tex


def parser_hooks():
	pdict = {}
	pdict['default_env'] = DefaultBlock.parse_env
	pdict['default_cmd'] = DefaultBlock.parse_cmd
	return pdict