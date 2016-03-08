import logging
from .Utilities import *
from .Block import Block

class NoOptCommand(Block):
    '''This class is for generic commands without options'''

    @staticmethod
    def parse(parser, tex, parent_block, params):
        block = NoOptCommand(params['cmd'],params['star'],
        		parent_block)
        logging.debug('NoOptCommand.parse @ cmd: %s',
        			params['cmd'])
        return (block,tex)

    def __init__(self, block_name, star, parent_block):
        super().__init__(block_name,'', parent_block)
        self.attributes['star']=star

parser_hooks = {
	'frontmatter' : NoOptCommand.parse,
	'mainmatter' : NoOptCommand.parse,
	'appendix' : NoOptCommand.parse,
	'backmatter' : NoOptCommand.parse
}