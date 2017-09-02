import logging
from ..Utilities import *
from .Block import Block

class NoOptCommandBlock(Block):
    '''This class is for generic commands without options'''

    @staticmethod
    def parse(parser, tex, parent_block, params):
        block = NoOptCommandBlock(params['cmd'],params['star'],
        		parent_block)
        return (block,tex)

    def __init__(self, block_name, star, parent_block):
        super().__init__(block_name,'', parent_block)
        self.attributes['star']=star

parser_hooks = {
	'frontmatter' : NoOptCommandBlock.parse,
	'mainmatter' : NoOptCommandBlock.parse,
	'appendix' : NoOptCommandBlock.parse,
	'backmatter' : NoOptCommandBlock.parse
}
