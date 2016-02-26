import logging
from . import utility
from . import CommandParser
from .Block import *

class ListBlock(Block):
    '''
    We use one Block type for all listings.
    Itemize, Enumerate, Description are
    specified in list_type attributes.
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
        list_type = params['env']
        block = ListBlock(list_type,
                tex, parent_block)
        logging.debug('ListBlock.parse @' )
        #parsing children blocks
        ch_blocks = parser.parse_instructions(
                tex, parent_block,{})
        #now we search for item blocks
        self.ciao = 3
        item_blocks = []
        for i,bl in enumerate(ch_blocks):
            if isinstance(bl,ItemBlock):
                item_blocks.append(bl)
                #all block until we reach another
                #item is added to the item block
                j = i
                while True:
                    if j+1 < len(ch_blocks):
                        bll = ch_blocks[j+1]
                        if isinstance(bll,ItemBlock):
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

    def __init__(self, list_type, tex, parent_block):
        super().__init__(list_type,tex,parent_block)
        #all information is in children blocks
        self.attributes['list_type'] = list_type



class ItemBlock(Block):
    '''This is only a place holder for a item.
    The itemize environment will add it his content.
    It's impossibile to extract it before'''

    @staticmethod
    def parse (parser, tex, parent_block, params):
        #we must search for the param \item [word]
        options, left_tex = CommandParser.parse_options(
            tex, [('word','[',']')])
        word = options['word']
        block = ItemBlock(word, parent_block)
        logging.debug('ItemBlock.parse @ word: %s',str(word))
        #the left_tex is returned stripped
        return (block, left_tex.strip())

    def __init__(self, word, parent_block):
        super().__init__('item',word,parent_block)
        #the word is the \item[word] part
        self.attributes['word'] = word

parser_hooks = {
    'itemize': ListBlock.parse,
    'enumerate': ListBlock.parse,
    'description': ListBlock.parse,
    'item': ItemBlock.parse,
}
