import re
import logging
from . import utility
from .Block import *

class TextBlock(Block):

    @staticmethod
    def parse_plain_text(parser ,tex, parent_block, options):
        logging.debug('TextBlock.parse_plain_text @ ')
        #first of all we can create the new block
        text_block = TextBlock(tex, parent_block)
        #the block is returned
        return (text_block,'')

    def parse_accents(parser, tex, parent_block, options):
        logging.debug('TextBlock.parse_plain_text @ ')
        #we can extract the letter using utility
        params = utility.get_command_greedy()

        

    def __init__(self, text, parent_block):
        '''
        Constructor for text:
        -text: string:
        '''
        super().__init__('text', parent_block)
        #attributes
        self.attributes['text'] = text
        self.attributes['text_lenght'] = len(text)

    def __str__(self):
        return  '<Block:{}, ID:{}, text_lenght:{}>'.format(
            self.block_name, self.id, self.attributes['text_lenght'])


parser_hooks = {
    'text': TextBlock.parse_plain_text,
    "'": TextBlock.parse_accents
    }