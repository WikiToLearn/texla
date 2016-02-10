import utility


def parser_hooks():
	pdict = {'default': Block.parse}
	return pdict


'''Base Block definition'''
class Block:

	@classmethod
	def parse(cls, tex, parent_block, options={}):
		pass

	def __init__(self, parent_block):
		self.parent_block = parent_block
		self.id = parent_block.id + '-' + utility.get_random_string(3)
		self.children_blocks = children_blocks
		#section level
		#by default the level is the same of parent block
		self.section_level = self.parent_block.section_level 

	'''
	IMPORTANT: this function is called by the self.parse fuction.
	It MUST NOT be called from outside, expecially the parser
	'''
	def add_children_block(self, block):
		self.children_blocks.append(block)