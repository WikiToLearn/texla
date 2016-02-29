from .Utilities import *

'''
Root block of the tree. It's a special
block and don't inherit from Block class
'''
class DocumentBlock():

	def __init__(self, title,  options):
		self.id = "@"
		self.title = title
		self.options = options
		self.parent_block = None
		self.section_level = -1
		self.tree_depth = -1
