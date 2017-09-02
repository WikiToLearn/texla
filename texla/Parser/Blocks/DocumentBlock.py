from ..Utilities import *
from .Block import *

'''
Root block of the tree. It's a special
block and don't inherit from Block class
'''
class DocumentBlock(Block):

    def __init__(self, title,  options):
        super().__init__('root-block','', None)
        self.title = title
        self.options = options
        self.section_level = -1
        self.tree_depth = -1
        self.attributes['title'] = title
