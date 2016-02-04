import os


class Parser:

	def __init__(self, tex):
		self.tex = tex


	def parse(self,tex):
		###TODO:preparsing

		#Getting content of \begin{document}
		r_doc = re.compile(r"\\begin(?P<options>\[.*?\])?{document}(?P<content>.*?)\\end{document}",
				re.DOTALL)
		m_doc = r_doc.search(tex)
		#getting content
		content = m_doc.groups("content")
		#creating root block
		self.root_block = documentBlock()
		#beginning of parsing 
		self.parser_cycle(self.root_block,content)

	def parser_cycle(self, block, tex):
		#first of all we search for section





def import_block_modules():
	for module in os.listdir("Blocks"):
		__import__(module)
		if hasattr(module,"register"):
			module.register()

import_block_modules()