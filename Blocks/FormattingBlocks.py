import logging
from .Utilities import *
from .Block import Block
	
#general class for every type of text format
class FormattingText(Block):

	@staticmethod
	def parse(parser, tex, parent_block, params):
		logging.debug('FormattingText.parse @ tex:', tex )
		options, left_tex = CommandParser.parse_options(tex,
			[('text','{','}')])
		text = options['text']
		block = FormattingText(params['cmd'], text, parent_block)
		ch_blocks = parser.parse_instructions(
				text, block, {})
		block.add_children_blocks(ch_blocks)
		return (block, left_tex)
			
	def __init__(self, format_type, text, parent_block):
		logging.debug('format type:', format_type )
		super().__init__('formatting_text',text,parent_block)
		self.attributes['text'] = text
		self.attributes['text_lenght'] = len(text)
		self.attributes['format_type'] = format_type


	
parser_hooks = {
	#fonts
	'underline' : FormattingText.parse,
	'textrm' : FormattingText.parse,
	'texttt' : FormattingText.parse,
	'textmd' : FormattingText.parse,
	'textup' : FormattingText.parse,
	'textsl' : FormattingText.parse,
	'emph' : FormattingText.parse,
	'textsf' : FormattingText.parse,
	'textbf' : FormattingText.parse,
	'textit' : FormattingText.parse,
	'textsc' : FormattingText.parse,
	'textnormal' : FormattingText.parse,
	'textsuperscript' : FormattingText.parse,
	'textsubscript' : FormattingText.parse
	#fontsize
	
}
