import logging
from ..Utilities import *
from .Block import Block

class ClearBlock(Block):
    '''Block that  ends the current page
    and causes all figures and tables that
    have so far appeared in the input to be printed'''

    @staticmethod
    def parse(parser, tex, parent_block, params):
        block = ClearBlock(params['cmd'], parent_block)
        return (block, tex)


    def __init__(self, clear_type, parent_block):
        super().__init__(clear_type, '', parent_block)

parser_hooks = {
    'clearpage' : ClearBlock.parse,
    'cleardoublepage' : ClearBlock.parse
    }
