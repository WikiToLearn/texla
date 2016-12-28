import re
import logging
from .Utilities import *
from .Block import Block

class SectionBlock(Block):

    @staticmethod
    def parse(parser, tex, parent_block, params):
        sec_level = params['sec_level']
        level_key = params['level_key']
        star = params['star']
        options, left_tex = CommandParser.parse_options(
                tex, [('index_title','[',']'),('title','{','}')])
        #the regex MUST MATCH if not the parse wouldn't be called
        title_text = options['title']
        index_title = options['index_title']
        #we have to parse possible commands in title looking for subblocks
        children_blocks = parser.parse_instructions(title_text, parent_block, {})
        title = ""
        if len(children_blocks)==1 and children_blocks[0].block_name == "text":
            title = children_blocks[0].content
        else:
            #looking for a text block
            blocks_to_check = children_blocks
            next_blocks = children_blocks
            while True:
                blocks_to_check = next_blocks
                next_blocks = []
                for chbl in blocks_to_check:
                    if chbl.block_name == "text":
                        title += chbl.content
                    else:
                        if len(chbl.ch_blocks)>0:
                            next_blocks += chbl.ch_blocks
                            break
                if len(next_blocks) == 0:
                    break

        logging.debug('SectionBlock.parse @ level: %s, title: %s',
            level_key, title)
        #first of all we can create the new block
        sec_block = SectionBlock(title, index_title,
            star, sec_level, parent_block)
        #now we can trigger the parsing of the content
        #of the section to get the children blocks.
        #the parser is called with options
        chld_blocks = parser.parse_sections(left_tex,
                sec_level,sec_block, {})
        #now we have all child blocks. They are simply added
        #to the list. no further processing for sections
        sec_block.add_children_blocks(chld_blocks)
        #the block is returned
        return sec_block


    def __init__(self, title, index_title, star, level, parent_block):
        '''
        Constructor for sections:
        -title: main title
        -index_title: title for table of content
        -star: True/False
        -level: sections level
        -parent_block
        '''
        #base constructor for Block. It created the id
        #nd basic data structures. Section has no content
        section_name = utility.section_level[level]
        super().__init__(section_name, None, parent_block)
        #new section level
        self.section_level = level
        #attributes
        self.attributes['section_name'] = section_name
        self.attributes['title'] = title
        self.attributes['index_title'] = index_title
        self.attributes['star'] = star

    def __str__(self):
        return  '<Block:{}, ID:{}, section_name:{}, title:{}>'.format(
            self.block_name, self.id, self.attributes['section_name'],
            self.attributes['title'])


parser_hooks = {
    'part': SectionBlock.parse,
    'chapter': SectionBlock.parse,
    'section': SectionBlock.parse,
    'subsection': SectionBlock.parse,
    'subsubsection': SectionBlock.parse,
    'paragraph': SectionBlock.parse,
    'subparagraph': SectionBlock.parse,
    }
