import logging
from ..Utilities import *
from .Block import Block
from .FormattingBlocks import *

class CommandsGroupBlock(Block):
    '''This block represents the syntax {...}.
    It is used to group formatting commands.
    These commands are parsed normally in FormattingBlocks.py
    and then catched by this block analyzing the ch_blocks.
    Formatting commands are saved inside formatting list
    as FormattingGroupBlock objects, ready for rendering.
    '''


    @staticmethod
    def parse(parser, tex, parent_block, params):
        options, left_tex = CommandParser.parse_options(tex,
            [('content','{','}')])
        content = options['content']
        block = CommandsGroupBlock(content, parent_block)
        ch_blocks = parser.parse_instructions(
                content, block, {})
        #searching Formatting Group block
        for ch in ch_blocks:
            if isinstance(ch, FormattingGroupBlock):
                #adding the formatting to the list of formatting
                block.formatting.append(ch)
            else:
                block.add_child_block(ch)
        return (block, left_tex)

    def __init__(self, content, parent_block):
        super().__init__('commands_group',content,parent_block)
        self.formatting = []


parser_hooks = {
    'commands_group' : CommandsGroupBlock.parse,
}
