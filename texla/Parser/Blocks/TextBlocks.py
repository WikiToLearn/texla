import re
import logging
from ..Utilities import *
from .Block import Block


class TextBlock(Block):
    @staticmethod
    def parse_plain_text(parser, tex, parent_block, params):
        '''Plain text is handled directly by the Parser as
        an environment. We have only to return
        the block'''
        #first of all we can create the new block
        text_block = TextBlock(tex, parent_block)
        #the block is returned
        return text_block

    def __init__(self, text, parent_block):
        '''
        Constructor for text:
        -text: string:
        '''
        super().__init__('text', text, parent_block)
        #attributes
        self.attributes['text'] = TextBlock.fix_text(text)
        self.attributes['text_length'] = len(text)

    @staticmethod
    def fix_text(text):
        '''Function that removes useless spaces from text'''
        text = text.replace('\t', '')
        text = text.replace('    ', '')
        return text

    def __str__(self):
        return '<Block:{}, ID:{}, text_length:{}>'.format(
            self.block_name, self.id, self.attributes['text_length'])


class AccentedLetterBlock(Block):
    @staticmethod
    def parse_accents(parser, tex, parent_block, params):
        accent_type = params['cmd']
        #we can extract the letter using grammar
        params, left_tex = CommandParser.parse_options(tex,
                                    [('letter', '{', '}')])
        #we get the letter, stripper to avoid spaces
        letter = params['letter'].strip()
        block = AccentedLetterBlock(letter, accent_type, parent_block)
        return (block, left_tex)

    def __init__(self, letter, accent_type, parent_block):
        super().__init__('accented_letter', letter, parent_block)
        self.attributes['letter'] = letter
        self.attributes['accent_type'] = accent_type

    def __str__(self):
        return '<Block:{}, ID:{}, accent:{}>'.format(
            self.block_name, self.id, self.attributes['accent_type'])


class SpecialCharacterBlock(Block):
    def parse(parser, tex, parent_block, params):
        block = SpecialCharacterBlock(params['cmd'], parent_block)
        return (block, tex)

    def __init__(self, char, parent_block):
        super().__init__(char, char, parent_block)
        self.attributes['character'] = char


parser_hooks = {
    'text': TextBlock.parse_plain_text,
    "'": AccentedLetterBlock.parse_accents,
    "`": AccentedLetterBlock.parse_accents,
    '"': AccentedLetterBlock.parse_accents,
    "~": AccentedLetterBlock.parse_accents,
    "^": AccentedLetterBlock.parse_accents,
    "=": AccentedLetterBlock.parse_accents,
    ".": AccentedLetterBlock.parse_accents,
    '%': SpecialCharacterBlock.parse,
    '&': SpecialCharacterBlock.parse,
    '{': SpecialCharacterBlock.parse,
    '}': SpecialCharacterBlock.parse,
    '#': SpecialCharacterBlock.parse,
    '_': SpecialCharacterBlock.parse,
    '$': SpecialCharacterBlock.parse
}
