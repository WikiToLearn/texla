import logging
from . import CommandParser
from .Block import *

class EmphBlock(Block):

	@staticmethod
	def parse(parser, tex, parent_block, options):
		logging.debug('EmphBlock.parse @ tex: %s', tex[:5]+'...' )
		params, left_tex = CommandParser.parse_command_options(tex,
			[('text','{','}')])
		text = params['text']
		block = EmphBlock(text, parent_block)
		return (block, left_tex)


	def __init__(self, text, parent_block):
		super().__init__('emph',parent_block)
		self.attributes['text'] = text
		self.attributes['text_lenght'] = len(text)


parser_hooks = {
	'emph': EmphBlock.parse
}
