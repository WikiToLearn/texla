'''Block for sectioning'''


class SectionBlock(Block):

	@staticmethod
	def register(parser_dict):
		parser_dict['part']= SectionBlock
		parser_dict['chapter']= SectionBlock
		parser_dict['section']= SectionBlock
		parser_dict['subsection']= SectionBlock
		parser_dict['subsubsection']= SectionBlock
		parser_dict['paragraph']= SectionBlock
		parser_dict['subparagraph']= SectionBlock

	@classmethod
	def parse(cls,text, parent_block):
		pass

	def __init__(self, parent_block, level, title, options={}):
		super().__init__(parent_block)
	
		self.level = level
		self.title = title

