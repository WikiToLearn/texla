import re
import logging
from .Utilities import *
from .Block import Block

class TextBlock(Block):

    @staticmethod
    def parse_plain_text(parser ,tex, parent_block, params):
        '''Plain text is seen as and env. It has only to return
        the block'''
        logging.debug('TextBlock.parse_plain_text @ %s',
            tex[:10].strip()+'...')
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
        self.attributes['text'] = text
        self.attributes['text_lenght'] = len(text)

    def __str__(self):
        return  '<Block:{}, ID:{}, text_lenght:{}>'.format(
            self.block_name, self.id, self.attributes['text_lenght'])


class AccentedLetterBlock(Block):

    @staticmethod
    def parse_accents(parser, tex, parent_block, params):
        accent_type = params['cmd']
        logging.debug('AccentedLetterBlock.parse @ ')
        #we can extract the letter using grammar
        params,left_tex = CommandParser.parse_options(tex,
            [('letter','{','}')])
        #we get the letter, stripper to avoid spaces
        letter = params['letter'].strip()
        block = AccentedLetterBlock(letter, accent_type, parent_block)
        return (block, left_tex)

    def __init__(self, letter, accent_type, parent_block):
        super().__init__('accented_letter',letter, parent_block)
        self.attributes['letter'] = letter
        self.attributes['accent_type'] = accent_type

    def __str__(self):
        return '<Block:{}, ID:{}, accent:{}>'.format(
            self.block_name, self.id,
            self.attributes['accent_type'])


class NewlineBlock(Block):

    def parse_newline(parser, tex, parent_block, params):
        logging.debug('NewlineBlock.parse @ ')
        block = NewlineBlock(params['star'], parent_block)
        left_tex = CommandParser.parse_options(tex,[])[1]
        return (block, left_tex)

    def __init__(self, star, parent_block):
        super().__init__('newline','\n', parent_block)
        self.attributes['text'] = '\n'
        self.attributes['star'] = star



class NewPageBlock(Block):

    @staticmethod
    def parse_newpage(parser, tex, parent_block, params):
        block = NewPageBlock(params['star'],
                 parent_block)
        logging.debug('NewPageBlock.parse_newpage @ cmd: %s',params['cmd'])
        return (block,tex)

    def __init__(self, star, parent_block):
        super().__init__('newpage','', parent_block)
        self.attributes['star']=star


class SpecialCharacterBlock(Block):

    def parse(parser, tex, parent_block, params):
        logging.debug('SpecialCharacter.parse @ char: %s ',
                        params['cmd'])
        block = SpecialCharacterBlock(params['cmd'], parent_block)
        return (block, tex)

    def __init__(self, char, parent_block):
        super().__init__('special-character',char, parent_block)
        self.attributes['character'] = char


parser_hooks = {
    'text': TextBlock.parse_plain_text,
    "'": AccentedLetterBlock.parse_accents,
    "`" : AccentedLetterBlock.parse_accents,
    '"' : AccentedLetterBlock.parse_accents,
    "~" : AccentedLetterBlock.parse_accents,
    "^" : AccentedLetterBlock.parse_accents,
    "=" : AccentedLetterBlock.parse_accents,
    "." : AccentedLetterBlock.parse_accents,
    '\\': NewlineBlock.parse_newline,
    '%' : SpecialCharacterBlock.parse,
    '&' : SpecialCharacterBlock.parse,
    '{' : SpecialCharacterBlock.parse,
    '}' : SpecialCharacterBlock.parse,
    '#' : SpecialCharacterBlock.parse,
    '_' : SpecialCharacterBlock.parse,
    '$' : SpecialCharacterBlock.parse,
    'newline': NewlineBlock.parse_newline,
    'newpage' : NewPageBlock.parse_newpage
    }
