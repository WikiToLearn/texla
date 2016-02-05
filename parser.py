import os

class Parser:

	def __init__(self, tex):
		self.tex = tex


	def parse(self,tex):
		###TODO:preparsing

		#Getting content of 
		m_doc = regexes.r_doc.search(tex)
		#getting content
		content = m_doc.groups("content")
		options = m_doc.groups("options")
		#creating root block
		self.root_block = documentBlock()
		#beginning of parsing 
		self.parser_cycle(self.root_block,content)

	def parser_cycle(self, block, tex):
		#first of all we search for sectioning



	def import_block_modules(self):
		self.parser_hooks={}
		for module in os.listdir("Blocks"):
			__import__(module)
			if hasattr(module,"parser_functions"):
				for key,value  in module.parser_functions.items():
					self.parser_functions[key] = value



