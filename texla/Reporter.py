from .Parser.TreeExplorer import TreeExplorer
import logging

class Reporter:

    def __init__(self, tree):
        self.tree_explorer = tree
        #registering the block_names
        self.tree_explorer.register_block_names()
        self.not_parsed_blocks = self.tree_explorer.block_names["default"]
        self.not_rendered_blocks = []
        self.not_parsed_types = {}
        self.not_rendered_types = {}
        for bl in self.not_parsed_blocks:
            if bl.type not in self.not_parsed_types:
                self.not_parsed_types[bl.type] = []
            self.not_parsed_types[bl.type].append(bl)


    def add_not_rendered_block(self, block):
        """This method saves a block that is not rendered by the Renderer."""
        self.not_rendered_blocks.append(block)
        if not block.block_name in self.not_rendered_types:
            self.not_rendered_types[block.block_name] = []
        self.not_rendered_types[block.block_name].append(block)

    def print_report(self, console=True):
        logging.info('\033[0;34m############### TEXLA REPORT  ###############\033[0m')
        s = []
        s.append("\n- NOT PARSED blocks:")
        for bl, v in self.not_parsed_types.items():
            s.append("\t- {} : {}".format(bl, len(v)))
        s.append("\n- NOT RENDERED blocks:")
        for bl, v in self.not_rendered_types.items():
            s.append("\t- {} : {}".format(bl, len(v)))
        text= "\n".join(s)
        if console:
            logging.info(text)
        #saving to file also the block trees
        with open("debug/texla_report.txt",'w') as file:
            t = ["############### TEXLA REPORT  ###############"]
            t.append("\n- NOT PARSED blocks:")
            for bl, v in self.not_parsed_types.items():
                t.append("\t- {} : {}".format(bl, len(v)))
            t.append("\n- NOT PARSED blocks details:")
            t.append(self.tree_explorer.print_tree_to_blocks(self.not_parsed_blocks))
            t.append("\n- NOT RENDERED blocks:")
            for bl, v in self.not_rendered_types.items():
                t.append("\t- {} : {}".format(bl, len(v)))
            t.append("\n- NOT RENDERED blocks details:")
            t.append(self.tree_explorer.print_tree_to_blocks(self.not_rendered_blocks))
            file.write("\n".join(t))
