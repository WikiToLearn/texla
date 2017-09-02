import logging
from ..Utilities import *
from .Block import Block

class FigureBlock(Block):
    '''Permission to place the float:
    h here at the very place in the text where it occurred.
    This is useful mainly for small floats.
    t at the top of a page
    b at the bottom of a page
    p on a special page containing only floats.
    ! without considering most of the internal parametersa,
    which could otherwhise stop this float from being placed.
    '''

    @staticmethod
    def parse_env(parser, tex, parent_block, params):
        options, left_tex = CommandParser.parse_options(tex,
              [('placement_specifier','[',']')])
        ps = 'tbp'
        if options['placement_specifier']:
            ps = options['placement_specifier']
        block = FigureBlock(ps, left_tex, parent_block)
        #now we parse the content
        children_blocks = parser.parse_instructions(left_tex, block, {})
        #now we can add the children nodes
        block.add_children_blocks(children_blocks)
        return block


    def __init__(self, placement_specifier, tex, parent_block):
        super().__init__('figure', tex, parent_block)
        self.attributes['placement_specifier'] = placement_specifier


class IncludeGraphicsBlock(Block):

    @staticmethod
    def parse(parser, tex, parent_block, params):
        options, left_tex = CommandParser.parse_options(tex,
                [('img_info','[',']'), ('img_name','{','}')])
        ar_img_info = {}
        if options['img_info']:
            str_splits = options['img_info'].split(
                ',', options['img_info'].count(','))
            for str_split in str_splits:
                spl = str_split.split('=', 1)
                ar_img_info[spl[0].strip(' ')] = spl[1].strip(' ')
        block = IncludeGraphicsBlock(options['img_name'],
                ar_img_info, left_tex, parent_block)
        return (block, left_tex)

    def __init__(self, img_name, ar_img_info, tex, parent_block):
        super().__init__('includegraphics', tex, parent_block)
        self.attributes['img_name'] = img_name
        self.attributes['img_options'] = ar_img_info



class CaptionBlock(Block):

    @staticmethod
    def parse(parser, tex, parent_block, params):
        options, left_tex = CommandParser.parse_options(tex,
                [('caption','{','}')])
        caption = options['caption']
        block = CaptionBlock(caption, parent_block)
        return (block, left_tex)

    def __init__(self, caption, parent_block):
        super().__init__('caption', caption, parent_block)
        self.attributes["caption"] = caption



parser_hooks = {
    'figure' : FigureBlock.parse_env,
    'includegraphics' :  IncludeGraphicsBlock.parse,
    'caption' : CaptionBlock.parse
}
