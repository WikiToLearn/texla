import re

'''Regex file'''

'''Regex to get content of \begin{document}\end{document}'''
r_doc = re.compile(r"\\begin(?P<options>\[.*?\])?{document}(?P<content>.*?)\\end{document}",re.DOTALL)

