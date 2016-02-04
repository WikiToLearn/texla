import os


class Parser:

	def __init__(self, tex):
		self.tex = tex

	




def import_block_modules():
	for module in os.listdir("Blocks"):
		__import__(module)
		if module.hasattribute()
		module.register()