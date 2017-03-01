import logging

class TreeExplorer:
    """
    The TreeExplorer class is an utility to navigate
    and extract information from the tree of parsed blocks.
    For example it is useful to extract the tree of the
    parents of a block for debugging reasons. It is useful
    also in rendering to localize blocks inside the document.
    """

    def __init__(self, root_block):
        """ The constructor needs a root_block to
        begin the tree"""
        self.root_block = root_block
        self.blocks = {'@': root_block}
        self.block_names = {}
        #registering blocks by id
        self.register_blocks(root_block.ch_blocks)

    @staticmethod
    def create_tree_from_children(block):
        #first of all we need the root_block
        current = block
        while True:
            if current.parent_block is None:
                root_block = current
                break
            current = current.parent_block
        #now we can return a new TreeExplorer
        #constructed from the found root.
        return TreeExplorer(root_block)

    def register_blocks(self, blocks):
        """This methods reads all the blocks tree
        from the root_block and created a dictionary
        with id:block"""
        for block in blocks:
            self.blocks[block.id] = block
            if block.N_chblocks > 0:
                self.register_blocks(block.ch_blocks)

    def update_blocks_register(self):
        """This methods update the blocks' ids register
        recalling register_blocks with the root_block"""
        self.register_blocks(self.root_block.ch_blocks)

    def get_parents_list(self, block):
        """This method returns the list of the parent
        blocks of the requested block """
        if isinstance(block, str):
            block = self.blocks[block]
        parents = []
        current = block
        while True:
            if current == self.root_block:
                break
            parents.append(current.parent_block)
            current = current.parent_block
        parents.reverse()
        return parents

    def get_parents_list_ids(self, block):
        parents = self.get_parents_list(block)
        return [x.id for x in parents]

    def get_block(self, blockid):
        return self.blocks.get(blockid)

    def print_tree(self, block, filter_list=None):
        """This methods prints a beautified tree starting
        from block parameter and his children. If filter_list
        is present only the block with the id in the list
        are printed. It returns a list of output strings"""
        output = []
        if filter_list is None or block.id in filter_list:
            lstr = ".    "* (block.tree_depth+1)
            output.append(lstr+ ".   "+ "  "+"_"*40 )
            output.append(lstr+ "#"+"---"+ ">|ID : {}".format(block.id))
            output.append(lstr+ ".   "+ " |block_name : {}".
                          format(block.block_name))
            output.append(lstr+ ".   "+ " |attributes: ")
            for at,attr in block.attributes.items():
                output.append(lstr+ ".   " + " |   - "+ "{} : {}".
                              format(at, attr))
            output.append(lstr+ ".   "+ " |content : {}".
                        format(block.content))
            output.append(lstr+ ".    ."+"\u203E"*40+"\n")
        output = "\n".join(output)
        #iterating on the block children
        for bl in block.ch_blocks:
            output += self.print_tree(bl, filter_list)
        return output

    def print_tree_to_blocks(self, blocks):
        """This methods print the tree of parents
        of the list of blocks passed as parameter.
        First of all it gets all the parents ids and
        then prints the tree using the list as filter."""
        fl = []
        for bl in blocks:
            fl+= self.get_parents_list_ids(bl)
            if isinstance(bl, str):
                fl.append(bl)
            else:
                fl.append(bl.id)
        return self.print_tree(self.root_block, filter_list=fl)

    def print_tree_to_block(self, block):
        return self.print_tree_to_blocks([block])

    def print_all_tree(self):
        return self.print_tree(self.root_block)

    def register_block_names(self):
        """This function registers the block_names, creating
         a dictionary with blocks groups by type"""
        self.block_names.clear()
        for bl in self.blocks.values():
            if not bl in self.block_names:
                self.block_names[bl.block_name] = []
            self.block_names[bl.block_name].append(bl)
