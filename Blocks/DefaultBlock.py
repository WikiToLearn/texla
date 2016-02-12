'''Default Block'''


def parser_hooks():
	pdict = {}
	pdict['default']= SectionBlock.parse
	return pdict

class DefaultBlock(Block):

	@staticmethod
	def parse(parser ,tex, parent_block, options):
		#default block is created
		block = DefaultBlock(tex, parent_block)
		#We cannot look inside tex, we don't know
		#what to parser.
		#we return the block
		return block
		

	'''
	Constructor for sections:
	-title: main title
	-index_title: title for table of content
	-numbered: True/False
	-level: sections level
	-parent_block
	'''
	def __init__(self, tex, parent_block):
		#base constructor for Block. It created the id 
		#nd basic data structures
		super().__init__('default', parent_block)
		self.tex = tex