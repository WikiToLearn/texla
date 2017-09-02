import logging
from ..Utilities import *
from .Block import Block

class FormattingTextBlock(Block):

    @staticmethod
    def parse(parser, tex, parent_block, params):
        options, left_tex = CommandParser.parse_options(tex,
            [('text','{','}')])
        text = options['text']
        block = FormattingTextBlock(params['cmd'], text, parent_block)
        ch_blocks = parser.parse_instructions(
                text, block, {})
        block.add_children_blocks(ch_blocks)
        return (block, left_tex)

    def __init__(self, format_type, text, parent_block):
        super().__init__(format_type,text,parent_block)
        self.attributes['text'] = text
        self.attributes['text_length'] = len(text)
        self.attributes['format_type'] = format_type

class FormattingGroupBlock(Block):
    '''This type of block is created for formatting
    commands used inside a {...} construct'''

    @staticmethod
    def parse(parser, tex, parent_block, params):
        block = FormattingGroupBlock(params['cmd'], parent_block)
        return (block, tex)

    def __init__(self, format_type, parent_block):
        super().__init__(format_type,'',parent_block)
        self.attributes['format_type'] = format_type


parser_hooks = {
    #fonts
    'underline' : FormattingTextBlock.parse,
    'uline' : FormattingTextBlock.parse,
    'uppercase' : FormattingTextBlock.parse,
    'textrm' : FormattingTextBlock.parse,
    'texttt' : FormattingTextBlock.parse,
    'textmd' : FormattingTextBlock.parse,
    'textup' : FormattingTextBlock.parse,
    'textsl' : FormattingTextBlock.parse,
    'emph' : FormattingTextBlock.parse,
    'textsf' : FormattingTextBlock.parse,
    'textbf' : FormattingTextBlock.parse,
    'textit' : FormattingTextBlock.parse,
    'textsc' : FormattingTextBlock.parse,
    'textlf' : FormattingTextBlock.parse,
    'textnormal' : FormattingTextBlock.parse,
    'textsuperscript' : FormattingTextBlock.parse,
    'textsubscript' : FormattingTextBlock.parse,
    #command in groups
    #shapes
    'normalfont' : FormattingGroupBlock.parse,
    'em' : FormattingGroupBlock.parse,
    'rmfamily' : FormattingGroupBlock.parse,
    'rm': FormattingGroupBlock.parse,
    'sffamily' : FormattingGroupBlock.parse,
    'sf': FormattingGroupBlock.parse,
    'ttfamily' : FormattingGroupBlock.parse,
    'tt': FormattingGroupBlock.parse,
    'upshape' : FormattingGroupBlock.parse,
    'up': FormattingGroupBlock.parse,
    'itshape' : FormattingGroupBlock.parse,
    'it': FormattingGroupBlock.parse,
    'slshape' : FormattingGroupBlock.parse,
    'sl': FormattingGroupBlock.parse,
    'scshape' : FormattingGroupBlock.parse,
    'sc': FormattingGroupBlock.parse,
    'bfseries' : FormattingGroupBlock.parse,
    'bf': FormattingGroupBlock.parse,
    'mdseries' : FormattingGroupBlock.parse,
    'md': FormattingGroupBlock.parse,
    'lfseries' : FormattingGroupBlock.parse,
    'lf': FormattingGroupBlock.parse,
    #sizes
    'tiny' : FormattingGroupBlock.parse,
    'scriptsize' : FormattingGroupBlock.parse,
    'footnotesize' : FormattingGroupBlock.parse,
    'small' : FormattingGroupBlock.parse,
    'normalsize' : FormattingGroupBlock.parse,
    'large' : FormattingGroupBlock.parse,
    'Large' : FormattingGroupBlock.parse,
    'LARGE' : FormattingGroupBlock.parse,
    'huge' : FormattingGroupBlock.parse,
    'Huge' : FormattingGroupBlock.parse,
}
