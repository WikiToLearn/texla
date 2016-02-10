'''Block for sectioning'''


def parser_hooks():
	pdict = {}
	pdict['part']= SectionBlock.parse
	pdict['chapter']= SectionBlock.parse
	pdict['section']= SectionBlock.parse
	pdict['subsection']= SectionBlock.parse
	pdict['subsubsection']= SectionBlock.parse
	pdict['paragraph']= SectionBlock.parse
	pdict['subparagraph']= SectionBlock.parse
	return pdict

class SectionBlock(Block):

	@classmethod
	def parse(cls,tex, parent_block, options):
		sec_level = options['sec_level']
		level_key = options['level_key'] 
		#we have to parse the section
		#first of all we can create the new block
		sec = SectionBlock()
		pass

	@staticmethod
	def parser_args(tex):
		


	def __init__(self, title, parent_block, level, options={}):
		super().__init__(parent_block)
	
		self.section_level = level
		self.title = title

