'''Block for sectioning'''


class SectionBlock(Block):

	@classmethod
	def parse(cls,text, parent_block):

	def __init__(self, parent_block, level, title):
		super().__init__(parent_block)
	
		self.level = level
		self.title = title

