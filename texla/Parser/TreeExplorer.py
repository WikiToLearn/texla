import logging

class TreeExplorer:
    '''
    The TreeExplorer class is an utility to navigate
    and extract information from the tree of parsed blocks.
    For example it is useful to extract the tree of the
    parents of a block for debugging reasons. It is useful
    also in rendering to localize blocks inside the document.
    '''

    def __init__(self, root_block):
        ''' The constructor needs a root_block to
        begin the tree'''
        self.root_block = root_block
        self.blocks = {'@': root_block}
        #registering blocks by id
        self.register_blocks(root_block.ch_blocks)

    def register_blocks(self, blocks):
        '''This methods reads all the blocks tree
        from the root_block and created a dictionary
        with id:block'''
        for block in blocks:
            self.blocks[block.id] = block
            if block.N_chblocks > 0:
                self.register_blocks(block.ch_blocks)

    def update_blocks_register(self):
        '''This methods update the blocks' ids register
        recalling register_blocks with the root_block'''
        self.register_blocks(self.root_block.ch_blocks)

    def get_parent_tree(self, block):
        '''This method returns the list of the parent
        blocks of the requested block'''
        parents = []
        current = block
        while True:
            if current == self.root_block:
                break
            parents.append(current.parent)
            current = current.parent
        return parents.reverse()

    def get_parent_tree_id(self, blockid):
        parents = []
        current = self.blocks[blockid]
        while True:
            if current == self.root_block:
                break
            parents.append(current.parent)
            current = current.parent
        return parents.reverse()

    def print_tree(self):
        for bl, blo in self.blocks.items():
            print("{} = {}".format(bl, blo))
