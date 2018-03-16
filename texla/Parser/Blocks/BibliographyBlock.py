import logging
from ..Utilities import *
from .Block import Block

class ThebibliographyBlock(Block):
    '''
    This block represents the Thebibliography environment
    '''

    @staticmethod
    def parse(parser, tex, parent_block, params):
        '''We parse the content of the env.
        Then we analyze the blocks and find
        which are items and not. The hierarchy of
        blocks is constructed after the parsing of
        the content. It's the only way to let the parser
        handle nested environments. Then, all the
        blocks are reappended under items blocks and
        added as children nodes.
        '''
        options, left_tex = CommandParser.parse_options(tex, [('opt',' {','}')])
        block = ThebibliographyBlock(options["opt"], tex, parent_block)
        #parsing children blocks
        ch_blocks = parser.parse_instructions(left_tex, parent_block,{})
        #now we search for item blocks
        item_blocks = []
        for i,bl in enumerate(ch_blocks):
            if isinstance(bl,BibitemBlock):
                item_blocks.append(bl)
                # Save the bibitem in the thebibliography map
                block.items[bl.attributes["label"]] = bl
                #all block until we reach another
                #item is added to the item block
                j = i
                while True:
                    if j+1 < len(ch_blocks):
                        bll = ch_blocks[j+1]
                        if isinstance(bll,BibitemBlock):
                            break
                        #changin parent
                        bll.change_parent_block(bl)
                        #adding block to
                        #item children
                        bl.add_child_block(bll)
                        j+=1
                    else:
                        break
        #adding items blocks to children
        block.add_children_blocks(item_blocks)
        return block

    def __init__(self, options, tex, parent_block):
        super().__init__("thebibliography",tex,parent_block)
        self.attributes["options"] = options
        self.items = {}


class BibitemBlock(Block):
    ''' This is a placeholder for a thebibliography
    environment entry'''

    @staticmethod
    def parse (parser, tex, parent_block, params):
        options, left_tex = CommandParser.parse_options(
            tex, [('label','{','}')])
        label =  options['label']
        block = BibitemBlock(label, parent_block)
        #if there's a column in the left text is removed
        return (block, left_tex.strip())

    def __init__(self, label, parent_block):
        super().__init__('bibitem', label,parent_block)
        self.attributes['label'] = label

    def __str__(self):
        return '<Block:{}, ID:{}, label: {}>'.format( 
            self.block_name, self.id, self.attributes["label"])

parser_hooks = {
    'thebibliography': ThebibliographyBlock.parse,
    'bibitem': BibitemBlock.parse
}
