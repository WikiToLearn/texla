import utility

'''Base Block definition'''
class Block:

	@staticmethod
	def register(parser_dict):
		parser_dict['default': Block.parse]

	@classmethod
	def parse(cls, text, parent_block):
		pass

	def __init__(self, parent_block):
		self.parent_block = parent_block
		self.id = parent_block.id + '-' + utility.get_random_string(3)
		self.leafs = children_blocks


