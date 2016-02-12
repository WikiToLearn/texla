'''Block for sectioning'''


def parser_hooks():
	pdict = {}
	pdict['part']= SectionBlock.parse
	pdict['chapter']= SectionBlock.parse
	pdict['section']= SectionBlock.parse
	pdict['subsection']= SectionBlock.parse
	pdict['subsubsection']= SectionBlock.parse
	pdict['paragraph']= SectionBlock.parse
	pdict['subparagraph']= SectionBlock.parse
	return pdict

class SectionBlock(Block):

	@staticmethod
	def parse(parser ,tex, parent_block, options):
		sec_level = options['sec_level']
		level_key = options['level_key'] 
		#we have to parse the section
		sec_re = re.compile(r'\\'+level_key+ r'(?P<ast>[*])?' \
			r'(?:\[(?P<index_title>.*?)\])?{(?P<title>.*?)}')
		m = sec.match(tex)
		#the regex MUST MATCH if not the parse wouldn't be called
		title = m.group('title')
		index_title = m.group('index_title')
		numbered = (m.group('ast')==None)
		#first of all we can create the new block
		sec_block = SectionBlock(title, index_title, 
			numbered, sec_level, parent_block)
		#now we can trigger the parsing of the content 
		#of the section to get the children blocks.
		content = tex[m.end():]
		#the parser is called with options
		poptions = {'parse_sections':True,
                   'parse_environments':True,
                   'sec_level': sec_level}
		chld_blocks = parser.parser_cycle(content, sec_block, poptions)
		#now we have all chld blocks. They are simply added to the list.
		#no further processing for sections
		sec_block.add_children_blocks(chld_blocks)
		#the block is returnes
		return sec_block
		

	'''
	Constructor for sections:
	-title: main title
	-index_title: title for table of content
	-numbered: True/False
	-level: sections level
	-parent_block
	'''
	def __init__(self, title, index_title, numbered, level, parent_block):
		#base constructor for Block. It created the id 
		#nd basic data structures
		super().__init__(parent_block)
		#new section level
		self.section_level = level
		#attributes
		self.attributes['title'] = title
		self.attributes['index_title'] = index_title
		self.attributes['numbered'] = numbered

