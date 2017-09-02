import logging
from ..Utilities import *
from .Block import Block
import re

class ListingsEnvironment(Block):

    @staticmethod
    def parse_environment(parser, tex, parent_block, params):
        opts , content = CommandParser.parse_options(tex,
                [('options', '[',']')])
        options = {}
        if (opts['options'] != None):
            for l in opts['options'].split(','):
                ll = l.strip().split('=')
                options[ll[0]] = ll[1]
        block = ListingsEnvironment('lstlisting', content, options, parent_block)
        return block

    @staticmethod
    def parse_options_command(parser, tex, parent_block, params):
        content, left_text = CommandParser.parse_options(tex,
                [('content', '{','}')])
        content = content['content']
        options = {}
        for l in re.compile(r',\s*\n').split(content):
            ll = l.strip().split('=')
            options[ll[0]] = ll[1]
        block = ListingsEnvironment('lstset', content, options, parent_block)
        return (block, left_text)


    def __init__(self, name, content, options,  parent_block):
        super().__init__(name, content, parent_block)
        self.options = options



parser_hooks = {
    "lstlisting": ListingsEnvironment.parse_environment,
    "lstset": ListingsEnvironment.parse_options_command
}
