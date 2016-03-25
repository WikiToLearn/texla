import logging
from .Utilities import *
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
        logging.debug('BreakBlock.parse')
        return (block, left_text)


    def __init__(self, break_type, priority, content, parent_block):
        super().__init__(break_type, content, parent_block)
        self.attributes['priority'] = priority

parser_hooks = {
    'linebreak' : BreakBlock.parse,
    'pagebreak' : BreakBlock.parse,
    'nolinebreak' : BreakBlock.parse,
    'nopagebreak' : BreakBlock.parse
    }
