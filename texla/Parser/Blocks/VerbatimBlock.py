import logging
import re
from ..Utilities import *
from .Block import Block

class VerbatimBlock(Block):
    '''Starts an enviroment which will be typeset exactly
    as you type it, carriage returns and all, usually in typewriter font'''

    @staticmethod
    def parse_verbatim(parser, tex, parent_block, params):
        #we first create the Block
        block = VerbatimBlock('verbatim', tex,
                        params['star'], parent_block)
        #there are no children 'cause it's verbatim
        return block

    @staticmethod
    def parse_verb(parser, tex, parent_block, params):
        #we have to extract the delimiter
        options, left_tex = CommandParser.parse_options(tex,
            [('content','{','}')])
        text = options['content']
        block = VerbatimBlock('verb',text,False, parent_block)
        return (block, left_tex)


    def __init__(self, vtype, content,star, parent_block):
        super().__init__(vtype, content, parent_block)
        self.attributes['content'] = content
        self.attributes['star'] = star

parser_hooks = {
    'verbatim' : VerbatimBlock.parse_verbatim,
    'verb': VerbatimBlock.parse_verb
}
