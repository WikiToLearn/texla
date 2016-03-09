import logging
from .Utilities import *
from .Block import Block

class SpaceBlock(Block):
    '''This class gives you the possibility to
        put a vertical or horizontal space of the
        lenght you want'''

    @staticmethod
    def parse(parser, tex, parent_block, params):

        options, left_text = CommandParser.parse_options(
            tex, [('lenght','{','}')])

        block = SpaceBlock(params['cmd'],
                lenght, parent_block)
        logging.debug('SpaceBlock.parse @')
        return (block, left_text)


    def __init__(self, space_type, lenght, parent_block):
        super().__init__(space_type, '', parent_block)
        self.attributes['lenght'] = lenght

parser_hooks = {
    'hspace' : SpaceBlock.parse,
    'vspace' : SpaceBlock.parse
    }