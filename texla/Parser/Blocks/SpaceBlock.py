import logging
from ..Utilities import *
from .Block import Block

class SpaceBlock(Block):
    '''This class gives you the possibility to
        put a vertical or horizontal space of the
        length you want'''

    @staticmethod
    def parse(parser, tex, parent_block, params):
        options, left_text = CommandParser.parse_options(
            tex, [('length','{','}')])
        block = SpaceBlock(params['cmd'],
                options['length'], params['star'], parent_block)
        return (block, left_text)


    def __init__(self, space_type, length, star, parent_block):
        super().__init__(space_type, '', parent_block)
        self.attributes['length'] = length
        self.attributes['star'] = star

parser_hooks = {
    'hspace' : SpaceBlock.parse,
    'vspace' : SpaceBlock.parse,
    'mandatory_space' : SpaceBlock.parse
    }
