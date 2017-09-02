import logging
from ..Utilities import *
from .Block import Block

class AbstractBlock(Block):
    '''This class handles the abstract environment'''

    @staticmethod
    def parse(parser, tex, parent_block, params):
        #we first create the Block
        block = AbstractBlock( tex, parent_block)
        #now we parse the content
        children_blocks = parser.parse_instructions(tex, block, {})
        #now we can add the children nodes
        block.add_children_blocks(children_blocks)
        return block

    def __init__(self, tex, parent_block):
        super().__init__('abstract', tex, parent_block)

parser_hooks = {
    'abstract' : AbstractBlock.parse
}
