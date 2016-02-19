import logging
from . import CommandParser
from .Block import *

class EmphBlock(Block):

	@staticmethod
	def parse(parser, tex, parent_block, params):
		logging.debug('EmphBlock.parse @ tex: %s', tex[:5]+'...' )
		options, left_tex = CommandParser.parse_options(tex,
			[('text','{','}')])
		text = options['text']
		block = EmphBlock(text, parent_block)
		#now we parse the content just to be sure
		ch_blocks = parser.parse_instructions(
				text, block, {})
		block.add_children_blocks(ch_blocks)
		return (block, left_tex)

	def __init__(self, text, parent_block):
		super().__init__('emph',text,parent_block)
		self.attributes['text'] = text
		self.attributes['text_lenght'] = len(text)


class UnderlineBlock(Block):

	@staticmethod
	def parse(parser, tex, parent_block, params):
		logging.debug('UnderlineBlock.parse @ tex: %s', tex[:5]+'...' )
		options, left_tex = CommandParser.parse_options(tex,
			[('text','{','}')])
		text = options['text']
		block = UnderlineBlock(text, parent_block)
		#now we parse the content just to be sure
		ch_blocks = parser.parse_instructions(
				text, block, {})
		block.add_children_blocks(ch_blocks)
		return (block, left_tex)

	def __init__(self, text, parent_block):
		super().__init__('underline',text,parent_block)
		self.attributes['text'] = text
		self.attributes['text_lenght'] = len(text)




parser_hooks = {
	'emph': EmphBlock.parse,
	'underline' : UnderlineBlock.parse
}
