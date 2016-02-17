import logging
from . import CommandParser
from .Block import *

class FootnoteBlock(Block):
	'''This class handles \footnote command'''

	@staticmethod
	def parse(parser, tex, parent_block, options):
		#we get the content and the left_tex
		params, left_tex = CommandParser.parse_options(tex,
			[('content','{','}')])
		content = params['content']
		#we first create the Block
		block = FootnoteBlock(content, parent_block)
		logging.debug('FootnoteBlock.parse @')
		#now we parse the content 
		children_blocks = parser.parse_instructions(
			content, block, {})
		#now we can add the children nodes
		block.add_children_blocks(children_blocks)
		return (block, left_tex)


	def __init__(self, tex, parent_block):
		super().__init__('footnote', tex, parent_block)


parser_hooks = {
	'footnote' : FootnoteBlock.parse,
}
