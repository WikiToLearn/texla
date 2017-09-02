from ..Utilities import *


"""Base Block definition"""
class Block:
    """
    Block general attributes:
    -block_name: the new of the "type" of the block
    -id: unique id for the block in the tree
    -parent_block: parent in the tree
    -attributes: a dictionary for description of the block.
        All useful parser data go into attributes
    -ch_blocks: a list of children_blocks
    -section_level: the position of the block compared to
        sectioning levels defined in utility.py

    Derived Block could add more attributes.
    """

    @staticmethod
    def parse(parser, tex, parent_block, params):
        """
        The method must return a tuple with the created
        Block and the last used index of tex string."""
        pass


    def __init__(self, block_name, content, parent_block):
        """
        Base constructor for Block.
        It saves the parent_block and block name and create
        the new id for the new block. It creates data structures
        like the attributed dictionary and children nodes list.
        It always saves a content variable.
        By default, it sets the section_level of the block
        to that of the parend_block.
        """
        self.block_name = block_name
        self.content = content
        if not parent_block is None:
            self.parent_block = parent_block
            self.id = parent_block.id + '-' + utility.get_random_string(3)
            #Section level:
            #by default the level is the same of parent block
            self.section_level = self.parent_block.section_level
            #depth in the tree
            self.tree_depth = self.parent_block.tree_depth+1
        else:
            #if this is the root block
            self.parent_block = None
            self.id = '@'
            self.section_level = -1
            self.tree_depth = 0
        #dictionary for attributes
        self.attributes = {}
        #list for childrend blocks
        self.ch_blocks = []
        self.N_chblocks = 0


    def add_child_block(self, block):
        """
        IMPORTANT: this function is called by the self.parse fuction.
        It MUST NOT be called from outside, expecially the parser
        """
        self.ch_blocks.append(block)
        self.N_chblocks +=1

    def add_children_blocks(self, blocks):
        """
        IMPORTANT: this function is called by the self.parse fuction.
        It MUST NOT be called from outside, expecially the parser
        """
        self.ch_blocks += blocks
        self.N_chblocks +=len(blocks)

    def change_parent_block(self, new_parent):
        """This function changes the parent of the
        block. It changes parent object, id, and tree_depth.
        The section level is not changes for consistency.
        All children are updated.
        """
        self.parent_block = new_parent
        #rebuiding id
        self.id = new_parent.id + '-' + utility.get_random_string(3)
        #the section level is not changed,
        #but tree_depth is updated
        self.tree_depth = new_parent. tree_depth + 1
        #now childrens are updated
        for ch in self.ch_blocks:
            ch.change_parent_block(self)

    def get_children(self, bl_name):
        """ This function return a list of children blocks
        corresponding to the requested type. If there are not
        children blocks of that type it returns a void list."""
        result = []
        for bl in self.ch_blocks:
            if bl.block_name == bl_name:
                result.append(bl)
        return result

    def __str__(self):
        return '<Block:{}, ID:{}>'.format( self.block_name, self.id)

    def to_json(self, level=0):
        """
        This functions create a json ouput that
        represents the tree of subblocks of the called block.
        """
        json = ''
        levelb = level+3
        json += (' '*level + '{\n')
        json += (' '*levelb + '"ID":"'+ self.id+'",\n')
        json += (' '*levelb + '"block_name":"'+ self.block_name+'",\n')
        json += (' '*levelb + '"N. ch_blocks":"'+ str(self.N_chblocks)+'",\n')
        json += (' '*levelb + '"tree_depth":"'+ str(self.tree_depth)+'",\n')
        for k,v in self.attributes.items():
            json += (' '*levelb + '"'+k+ '":"'+str(v)+ '",\n' )
        json += (' '*levelb + '"children_blocks":[\n')
        for b in self.ch_blocks:
            json+= b.to_json(levelb+3)
        json += (' '*levelb+'],\n')
        json += (' '*level + '}\n')
        return json

    def n_children_blocks_total(self):
        """This function returns the
        number of all children blocks recursively."""
        n = len(self.ch_blocks)
        for c in self.ch_blocks:
            n+= c.n_children_blocks_total()
        return n

    def get_content(self):
        """
        This function can be overrided by a specific
        block in order to provide a personalized representation
        of the content of the block for logging/reporting.
        """
        return self.content

    def query_children_blocks(self, block_name, depth_first=False):
        """
        This function looks for a block with a specific block_name
        in the children of the block. If depth_first=True it recursiverly
        check in every children before continuing.
        """
        results = []
        for block in self.ch_blocks:
            if block.block_name == block_name:
                results.append(block)
            if depth_first:
                results += block.query_children_blocks(block_name, depth_first)
        if not depth_first:
            for bl in self.ch_blocks:
                results += bl.query_children_blocks(block_name, depth_first)
        return results
