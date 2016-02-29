import logging
import re
from .Utilities import *
from .Block import Block

'''Dictionary of parsed Theorems.
These data will be useful during the rendering of occurrences
of Theorems. Every theorem block memorize useful information
about them.'''
parsed_theorems = {}

class Theorem():
    ''' This object represents a theorem defined
    by the user'''

    def __init__(self, name, definition,star,
                 counter,numberby, title=''):
        self.name = name
        self.definition = definition
        self.star = star
        self.counter = counter
        self.numberby = numberby
        self.title = title

class TheoremBlock(Block):
    ''' The theorem block represts a theorem.
    The different type of theorems defined by the
    writer are preparsed and put into parser_theorems.
    The TheoremBlock saves the found theorem with its
    title and theorem type object '''

    @staticmethod
    def parse(parser, tex, parent_block, params):
        #first of all we extract the optional title
        data ,left_tex = CommandParser.parse_options(tex,
                    [('name','{','}'),('title','[',']')])
        name = data['name']
        title = data['title']
        block = TheoremBlock(parsed_theorems[name],
                    title, left_tex, parent_block)
        ch_blocks = parser.parse_instructions(left_tex,
                        block, {})
        block.add_children_blocks(ch_blocks)
        logging.debug('TheoremBlock.parse @ name: %s',name)
        return block

    def __init__(self, theorem, title, content, parent_block):
        super().__init__('theorem', content, parent_block)
        self.theorem = theorem
        self.title = title
        self.attributes['title'] = title
        self.attributes['th_name'] = theorem.name
        self.attributes['definition'] = theorem.definition
        self.attributes['star'] = theorem.star

class ProofBlock(Block):
    '''Block that represents a proof.'''

    @staticmethod
    def parse(parser, tex, parent_block, params):
        data ,left_tex = CommandParser.parse_options(tex,
                    [('title','[',']')])
        title = data['title']
        block = ProofBlock(title, left_tex, parent_block)
        ch_blocks = parser.parse_instructions(left_tex,
                        block, {})
        block.add_children_blocks(ch_blocks)
        logging.debug('ProofBlock.parse @ title: %s', title)
        return block

    def __init__(self, title, content, parent_block):
        super().__init__('proof',content,parent_block)
        self.title = title
        self.attributes['title'] = title


parser_hooks = {
    'theorem' : TheoremBlock.parse,
    'proof' : ProofBlock.parse
}
