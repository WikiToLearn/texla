import logging
from . import CommandParser
from .Block import *

class FootnoteBlock(Block):
	'''This class handles \footnote command'''

	@staticmethod
	def parse(parser, tex, parent_block, options):
		#we get the content and the left_tex
		print(tex)
		params, left_tex = CommandParser.parse_options(tex,
			[('content','{','}')])
		content = params['content']
		print(content)
		#we first create the Block
		block = FootnoteBlock(content, parent_block)
		logging.debug('FootnoteBlock.parse @')
		#now we parse the content 
		poptions = {'parse_sections':False,
                   'parse_envs':True,
                   'parse_commands':True,
                   'parse_math':True, }
		children_blocks = parser.parser_cycle(content, block, poptions)
		#now we can add the children nodes
		block.add_children_blocks(children_blocks)
		return (block, left_tex)


	def __init__(self, tex, parent_block):
		super().__init__('footnote', tex, parent_block)


parser_hooks = {
	'footnote' : FootnoteBlock.parse,
}
