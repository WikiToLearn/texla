import logging
from ..Utilities import *
from .Block import Block

class FootnoteBlock(Block):
	'''This class handles \footnote command'''

	@staticmethod
	def parse(parser, tex, parent_block, params):
		#we get the content and the left_tex
		options, left_tex = CommandParser.parse_options(tex,
			[('content','{','}')])
		content = options['content']
		#we first create the Block
		block = FootnoteBlock(content, parent_block)
		#now we parse the content
		children_blocks = parser.parse_instructions(
			content, block, {})
		#now we can add the children nodes
		block.add_children_blocks(children_blocks)
		return (block, left_tex)

	def __init__(self, tex, parent_block):
		super().__init__('footnote', tex, parent_block)


class QuotationBlock(Block):

	@staticmethod
	def parse(parser, tex, parent_block, params):
		#we first create the Block
		block = QuotationBlock(tex, params['env'], parent_block)
		#now we parse the content
		children_blocks = parser.parse_instructions(
			tex, block, {})
		#now we can add the children nodes
		block.add_children_blocks(children_blocks)
		return block

	def __init__(self, tex, quote_type, parent_block):
		super().__init__('quotation', tex, parent_block)
		self.quote_type = quote_type
		self.attributes['quote_type'] = quote_type


parser_hooks = {
	'footnote' : FootnoteBlock.parse,
	'quotation' : QuotationBlock.parse,
	'quote' : QuotationBlock.parse,
	'verse' : QuotationBlock.parse
}
