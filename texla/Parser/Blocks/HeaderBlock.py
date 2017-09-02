from .Block import Block
from ..Utilities import *
import logging
import re


class HeaderBlock(Block):
    '''This class get title,author and date at the beginning of tex'''

    @staticmethod
    def parse(parser, tex, parent_block, params):
        title = parser.doc_data['title']
        author = parser.doc_data['author']
        date = parser.doc_data['date']
        block = HeaderBlock(title, date, author, parent_block)
        return (block, tex)

    def __init__(self, title, date, author, parent_block):
        super().__init__('maketitle', '', parent_block)
        self.attributes['title'] = title
        self.attributes['author'] = author
        self.attributes['date'] = date



parser_hooks = {
    'maketitle': HeaderBlock.parse,
}
