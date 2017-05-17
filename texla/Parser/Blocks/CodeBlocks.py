import logging
from .Utilities import *
from .Block import Block

class ListingsEnvironment(Block):

    @staticmethod
    def parse_environment(parser, tex, parent_block, params):
        opts , content = CommandParser.parse_options(tex,
                [('options', '[',']')])
        options = {}

        if (opts['options'] != None):
            for l in opts['options'].split(','):
                ll = l.split('=')
                options[ll[0].strip()] = ll[1].strip()
        block = ListingsEnvironment(content, options, parent_block)
        return block      
          

    def __init__(self, content, options,  parent_block):
        super().__init__('lstlisting', content, parent_block)
        self.options = options



parser_hooks = {
    "lstlisting": ListingsEnvironment.parse_environment
}
