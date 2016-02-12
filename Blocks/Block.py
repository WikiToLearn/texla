from . import utility

def parser_hooks():
	pdict = {'default': Block.parse}
	return pdict


'''Base Block definition'''
class Block:

	@staticmethod
	def parse(parser, tex, parent_block, options={}):
		pass

	
	def __init__(self, block_name, parent_block):
		'''
		Base constructor for Block. 
		It saves the parent_block and block name and create  
		the new id for the new block. It creates data structures 
		like the attributed dictionary and children nodes list.
		By default, it sets the section_level of the block 
		to that of the parend_block.
		'''
		self.block_name = block_name
		self.parent_block = parent_block
		self.id = parent_block.id + '-' + block_name +\
				'@' + utility.get_random_string(3)
		#dictionary for attributes
		self.attributes = {}
		#list for childrend blocks
		self.children_blocks = []
		#Section level:
		#by default the level is the same of parent block
		self.section_level = self.parent_block.section_level 

	'''
	IMPORTANT: this function is called by the self.parse fuction.
	It MUST NOT be called from outside, expecially the parser
	'''
	def add_child_block(self, block):
		self.children_blocks.append(block)

	def add_children_blocks(self, blocks):
		self.children_blocks += blocks