import logging
from ..Utilities import *
from .Block import Block


class CiteBlock(Block):
    ''' Block for citation'''

    @staticmethod
    def parse (parser, tex, parent_block, params):
        options, left_tex = CommandParser.parse_options(
            tex, [('labels','{','}')])
        labels = [l.strip() for l in options['labels'].split(',')]
        block = CiteBlock(labels, parent_block)
        #if there's a column in the left text is removed
        return (block, left_tex)

    def __init__(self, labels, parent_block):
        super().__init__('cite', ",".join(labels), parent_block)
        self.attributes['labels'] = labels

parser_hooks = {
    'cite': CiteBlock.parse
}
