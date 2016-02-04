import utility

'''Root block of the tree'''
class DocumentBlock(Block):

	def __init__(self, options):
		self.id = "root"
		self.options = options
