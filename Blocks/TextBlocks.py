import re
import logging
from . import utility
from . import CommandParser
from .Block import *

class TextBlock(Block):

    @staticmethod
    def parse_plain_text(parser ,tex, parent_block, options):
        logging.debug('TextBlock.parse_plain_text @ %s', tex[:10]+'...')
        #first of all we can create the new block
        text_block = TextBlock(tex, parent_block)
        #the block is returned
        return (text_block,'')

    def __init__(self, text, parent_block):
        '''
        Constructor for text:
        -text: string:
        '''
        super().__init__('text', text, parent_block)
        #attributes
        self.attributes['text'] = text
        self.attributes['text_lenght'] = len(text)

    def __str__(self):
        return  '<Block:{}, ID:{}, text_lenght:{}>'.format(
            self.block_name, self.id, self.attributes['text_lenght'])


class AccentedLetterBlock(Block):
    
    def parse_accents(parser, tex, parent_block, options):
        logging.debug('TextBlock.parse_plain_text @ ')
        #we can extract the letter using grammar
        params,left_tex = CommandParser.parse_command_options(tex,
            [('letter','{','}')])
        #we get the letter
        letter = params['letter']
        block = AccentedLetterBlock(letter, parent_block)
        return (block, left_tex)
        
    def __init__(self, letter, parent_block):
        super().__init__('accented_letter',letter, parent_block)
        self.attributes['letter'] = letter


parser_hooks = {
    'text': TextBlock.parse_plain_text,
    "'": AccentedLetterBlock.parse_accents
    }