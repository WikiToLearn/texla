import re

'''
This function split the tex inside a list of tuples with
(type, content). The type could be text, display_math, inline_math.
The function is able to extract math inside \(...\) $...$ (inline) and
inside \[...\] $$...$$ (display).
'''
def math_tokenizer(tex):
	inline_re = re.compile(r'(?<![\$])\$([^$]+)\$(?!\$)', re.DOTALL)
	display_re = re.compile(r'(?<![\$])\$\$([^$]+)\$\$(?!\$)', re.DOTALL)
	inline_re2 = re.compile(r'\\\((.*?)\\\)',re.DOTALL)
	display_re2 = re.compile(r'\\\[(.*?)\\\]', re.DOTALL)
	#first of all we match a save the pos
	pos = {}
	for mi in inline_re.finditer(tex):
		pos[mi.start()] = ('inline_math',mi)
	for md in display_re.finditer(tex):
		pos[md.start()] = ('display_math',md)
	for mi2 in inline_re2.finditer(tex):
		pos[mi2.start()] = ('inline_math',mi2)
	for md2 in display_re2.finditer(tex):
		pos[md2.start()] = ('display_math',md2)
	#now we sort the dictionary
	tokens = []
	last_tex_index = 0
	for start in sorted(pos.keys()):
		end = pos[start][1].end()
		typ = pos[start][0]
		content = pos[start][1].group()
		previous_tex = tex[last_tex_index : start]
		tokens.append(('text', previous_tex))
		#the last_tex_index is moved forward
		last_tex_index = end
		#the match is saved
		tokens.append((typ, content))
	return tokens



a= open('test_math.tex','r').read()

l = math_tokenizer(a) 
for i in l:
	print (i)
