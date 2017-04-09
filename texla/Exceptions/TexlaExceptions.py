from ..Parser.TreeExplorer import  TreeExplorer

class TexlaError(Exception):
    pass

class PreparserError(TexlaError):

    def __init__(self, error_tex="", all_tex=""):
        self.error_tex = error_tex
        self.all_tex = all_tex

    def print_error(self):
        output = ["#"*50 + "\nCRASH REPORT\n" +"-"*30,
                  "ERROR TEX: " + self.error_tex]
        return "\n".join(output)

class PreparseMacrosError(PreparserError):
    pass

class ParserError(TexlaError):
    def __init__(self, error_tex, block, message):
        self.error_tex = error_tex
        self.block = block
        self.message = message
        #creating tree explorer
        self.tree_explorer = TreeExplorer.create_tree_from_children(block)

    def print_error(self):
        output = ["#" * 50 + "\nCRASH REPORT\n" + "-" * 30]
        output.append("\nMESSAGE: " + self.message)
        if len(self.error_tex) < 200:
            output.append("\nERROR TEX: " + self.error_tex)
        else:
            output.append("\nERROR TEX: " + self.error_tex[:200])
        output.append(self.tree_explorer.print_tree_to_block(self.block))
        print("\n".join(output))

    def print_complete_tree(self, path=None):
        if path:
            with open(path, 'w') as f:
                f.write(self.tree_explorer.print_all_tree())
        else:
            print(self.tree_explorer.print_all_tree())



class BlockError(ParserError):
    def __init__(self, block_type, error_tex, block, message):
        self.block_type = block_type
        self.error_tex = error_tex
        self.block = block
        self.message = message
        #creating tree explorer
        self.tree_explorer = TreeExplorer.create_tree_from_children(block)

    def print_error(self):
        output = ["#" * 50 + "\nCRASH REPORT\n" + "-" * 30]
        output.append("\nMESSAGE: " + self.message)
        if len(self.error_tex) < 200:
            output.append("\nERROR TEX: " + self.error_tex)
        else:
            output.append("\nERROR TEX: " + self.error_tex[:200])
        output.append("\nBLOCK TYPE: " + self.block_type)
        output.append(self.tree_explorer.print_tree_to_block(self.block))
        print("\n".join(output))
