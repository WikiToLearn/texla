import logging
from ...Exceptions.TexlaExceptions import *
from ..Utilities import *
from .Block import Block

'''Dictionary of parsed Theorems.
These data will be useful during the rendering of occurrences
of Theorems. Every theorem block memorize useful information
about them.'''
parsed_theorems = {}

class Theorem():
    ''' This object represents a theorem defined
    by the user'''

    def __init__(self, th_type, definition,star,
                 counter,numberby, title=''):
        self.th_type = th_type
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
                    [('th_type','{','}'),('title','[',']')])
        th_type = data['th_type']
        title = data['title']
        if th_type not in parsed_theorems:
            raise BlockError("theorem", tex, parent_block,
                             "Theorem type not found between preparsed ones")
        block = TheoremBlock(parsed_theorems[th_type],
                    title, left_tex, parent_block)
        ch_blocks = parser.parse_instructions(left_tex,
                        block, {})
        block.add_children_blocks(ch_blocks)
        return block

    def __init__(self, theorem, title, content, parent_block):
        super().__init__('theorem', content, parent_block)
        self.theorem = theorem
        self.th_type = theorem.th_type
        self.attributes['title'] = title
        self.attributes['type'] = theorem.th_type
        self.attributes['definition'] = theorem.definition
        self.attributes['star'] = theorem.star
        self.attributes['counter'] = theorem.counter

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
        return block

    def __init__(self, title, content, parent_block):
        super().__init__('proof',content,parent_block)
        self.title = title
        self.attributes['title'] = title


parser_hooks = {
    'theorem' : TheoremBlock.parse,
    'proof' : ProofBlock.parse
}
