'''Block for sectioning'''


class SectionBlock(Block):

	@staticmethod
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

	@classmethod
	def parse(cls,tex, parent_block):
		pass

	def __init__(self, parent_block, level, title, options={}):
		super().__init__(parent_block)
	
		self.section_level = level
		self.title = title

