import logging
from .Utilities import *
from .Block import Block

class VerbatimBlock(Block):
    '''Starts an enviroment which will be typeset exactly
    as you type it, carriage returns and all, usually in typewriter font'''

    @staticmethod
    def parse_verbatim(parser, tex, parent_block, params):
        #we first create the Block
        block = VerbatimBlock(tex, params['star'], parent_block)
        logging.debug('VerbatimBlock.parse_env @')
        #there are no children 'cause it's verbatim
        return block

    def __init__(self, content,star, parent_block):
        super().__init__('verbatim', content, parent_block)
        self.attributes['content'] = content
        self.attributes['star'] = star

parser_hooks = {
    'verbatim' : VerbatimBlock.parse_verbatim
}
