from .Parser.TreeExplorer import TreeExplorer
import logging

class Reporter:

    def __init__(self, tree):
        self.tree_explorer = tree
        self.not_parsed_blocks = self.tree_explorer.block_names["default"]
        self.not_rendered_blocks = []
        self.not_parsed_types = {}
        self.not_rendered_types = {}
        #collecting not parsed block types
        for bl in self.not_parsed_blocks:
            if bl.type not in self.not_parsed_types:
                self.not_parsed_types[bl.type] = []
            self.not_parsed_types[bl.type].append(bl)
        #references to labels not defined
        self.missing_anchors = {}


    def add_not_rendered_block(self, block):
        """This method saves a block that is not rendered by the Renderer."""
        self.not_rendered_blocks.append(block)
        if not block.block_name in self.not_rendered_types:
            self.not_rendered_types[block.block_name] = []
        self.not_rendered_types[block.block_name].append(block)

    def add_missing_anchor(self, label, refs):
        """This methods saves the references list to a missing label"""
        if label not in self.missing_anchors:
            self.missing_anchors[label] = []
        self.missing_anchors[label] += refs

    def print_report(self, console=True):
        logging.info('\033[0;34m############### TEXLA REPORT  ###############\033[0m')
        s = []
        s.append("\n- NOT PARSED blocks:")
        for bl, v in self.not_parsed_types.items():
            s.append("\t- {} : {}".format(bl, len(v)))
        s.append("\n- NOT RENDERED blocks:")
        for bl, v in self.not_rendered_types.items():
            s.append("\t- {} : {}".format(bl, len(v)))
        s.append("\n- Missing labels:")
        for lb in self.missing_anchors:
            s.append("\t- {}".format(lb))
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
            t.append("\n- Missing labels details:")
            for lb, refs in self.missing_anchors.items():
                t.append("\t- {}".format(lb))
                for ref in refs:
                    t.append("\t\t- {}".format(ref))
            file.write("\n".join(t))
