'''Base Block definition'''
class Block:

	@staticmethod
	def register(parser_dict):
		parser_dict['default': Block.parse]

	@classmethod
	def parse(cls, text):
		pass

	def __init__(self, content):
		self.content = content

