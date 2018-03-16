import logging
from ..Utilities import *
from .Block import Block


class CiteBlock(Block):
    ''' Block for citation'''

    @staticmethod
    def parse (parser, tex, parent_block, params):
        options, left_tex = CommandParser.parse_options(
            tex, [('label','{','}')])
        label =  options['label']
        block = CiteBlock(label, parent_block)
        #if there's a column in the left text is removed
        return (block, left_tex)

    def __init__(self, label, parent_block):
        super().__init__('cite', label,parent_block)
        self.attributes['label'] = label

    def __str__(self):
        return '<Block:{}, ID:{}, label: {}>'.format( 
            self.block_name, self.id, self.attributes["label"])

parser_hooks = {
    'cite': CiteBlock.parse
}
