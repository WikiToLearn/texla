import logging
from ..Utilities import *
from .Block import Block

class BreakBlock(Block):
    '''This class gives you the possibility to
        break/not break a line/page'''
    @staticmethod
    def parse(parser, tex, parent_block, params):
        options, left_text = CommandParser.parse_options(
            tex, [('priority','[',']')])
        if options['priority']==None:
            priority = 0
        else:
            priority = int(options['priority'])

        block = BreakBlock(params['cmd'],
                priority ,tex, parent_block)
        return (block, left_text)


    def __init__(self, break_type, priority, content, parent_block):
        super().__init__(break_type, content, parent_block)
        self.attributes['priority'] = priority


class NewlineBlock(Block):

    def parse_newline(parser, tex, parent_block, params):
        block = NewlineBlock(params['star'], parent_block)
        left_tex = CommandParser.parse_options(tex,[])[1]
        return (block, left_tex)

    def __init__(self, star, parent_block):
        super().__init__('newline','\n', parent_block)
        self.attributes['text'] = '\n'
        self.attributes['star'] = star


class NewPageBlock(Block):

    @staticmethod
    def parse_newpage(parser, tex, parent_block, params):
        block = NewPageBlock(params['star'],
                 parent_block)
        return (block,tex)

    def __init__(self, star, parent_block):
        super().__init__('newpage','', parent_block)
        self.attributes['star']=star

class ParBlock(Block):
    ''' This block only represents a \n\n in the tex'''
    @staticmethod
    def parse(parser, tex, parent_block, params):
        return (ParBlock(parent_block), tex)

    def __init__(self, parent_block):
        super().__init__('par','',parent_block)


parser_hooks = {
    '\\': NewlineBlock.parse_newline,
    'newline': NewlineBlock.parse_newline,
    'newpage' : NewPageBlock.parse_newpage,
    'linebreak' : BreakBlock.parse,
    'pagebreak' : BreakBlock.parse,
    'nolinebreak' : BreakBlock.parse,
    'nopagebreak' : BreakBlock.parse,
    'par' : ParBlock.parse
    }
