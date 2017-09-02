import logging
from ..Utilities import *
from .Block import Block

class DotsBlock(Block):

    @staticmethod
    def parse(parser, tex, parent_block, params):
        dot_type = params['cmd']
        block = DotsBlock(dot_type, parent_block)
        return (block, tex)

    def __init__(self, dot_type, parent_block):
        super().__init__('dots', '', parent_block)
        self.dot_type = dot_type
        self.attributes['dot_type'] = dot_type

    def __str__(self):
        return '<Block:{}, ID:{}, dot_type:{}>'.format(
                self.block_name, self.id, self.dot_type)

parser_hooks = {
    'dots' : DotsBlock.parse,
    'ldots' : DotsBlock.parse
}
