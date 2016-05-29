import logging
import re
from .Utilities import *
from .Block import Block

class VerbatimBlock(Block):
    '''Starts an enviroment which will be typeset exactly
    as you type it, carriage returns and all, usually in typewriter font'''

    @staticmethod
    def parse_verbatim(parser, tex, parent_block, params):
        #we first create the Block
        block = VerbatimBlock('verbatim', tex,
                        params['star'], parent_block)
        logging.debug('VerbatimBlock.parse_env @')
        #there are no children 'cause it's verbatim
        return block

    @staticmethod
    def parse_verb(parser, tex, parent_block, params):
        #we have to extract the delimiter
        delim = tex[0]
        r = re.compile(r'['+delim +r']'+\
                       r'(.*?)' + r'['+delim +r']')
        m = r.match(tex)
        block = VerbatimBlock('verb',m.group(1),False, parent_block)
        return (block, tex[m.end():])


    def __init__(self, vtype, content,star, parent_block):
        super().__init__(vtype, content, parent_block)
        self.attributes['content'] = content
        self.attributes['star'] = star

parser_hooks = {
    'verbatim' : VerbatimBlock.parse_verbatim,
    'verb': VerbatimBlock.parse_verb
}
