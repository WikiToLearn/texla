import logging
import re
from . import utility
from . import CommandParser
from .ReferenceBlocks import LabelBlock
from .Block import *

class MathBlock(Block):

    @staticmethod
    def parse_math_env(parser, tex, parent_block, params):
        ''' This parse hook it's used for $$, $, \[ \( and
        general math environments'''
        env = params['env']
        star = params.get('star',False)
        #getting labels and tex without labels
        tex, labels = MathBlock.parse_labels(tex)
        #the content of the math is stripped
        block = MathBlock(env, star, tex.strip(), parent_block)
        logging.debug('MathBlock.parse_math_env @ env: %s', env)
        #creating and adding labels blocks
        for l in labels:
            lblock = LabelBlock(l, block)
            logging.info('BLOCK @ %s%s', 
                    "\t"*lblock.tree_depth, str(lblock))
            block.add_child_block(lblock)
        return block

    @staticmethod
    def parse_ensure_math(parser, tex, parent_block, params):
        ''' The \ensuremath{} is a math command, not env'''
        options, left_tex = CommandParser.parse_options(tex,
            [('math','{','}')])
        text = options['math']
        block = MathBlock('ensuremath', False, text, parent_block)
        logging.debug('MathBlock.parse_ensure_math')
        return (block, left_tex)

    @staticmethod
    def parse_labels(tex):
        '''
        The function get labels from math. 
        Multiple labels in math are allowed.
        It creates a list of Label mathced and removes 
        them from the tex.
        It returns the modified tex and list of labels.
        '''
        lre = re.compile(r'\\label\s*\{(?P<label>.*?)\}')
        labels = []
        for m in lre.finditer(tex):
            labels.append(m.group('label'))
            #removing label from tex
            tex = tex.replace(m.group(), '')
        return (tex, labels)


    def __init__(self, math_type, star, tex, parent_block):
        super().__init__(math_type, tex, parent_block)
        #the type and content is saved both as attribute and instance member
        self.math_type = math_type
        self.attributes['math_type'] = math_type
        #the content is saved in attributes
        self.attributes['content'] = tex
        self.attributes['star'] = star

    def __str__(self):
        return  '<Block:{}, ID:{}, math_type:{}, star:{}>'.format(
            self.block_name, self.id, self.attributes['math_type'],
            self.attributes['star'])


parser_hooks = {
    'inline_math' : MathBlock.parse_math_env,
    'display_math' : MathBlock.parse_math_env,
    'equation' : MathBlock.parse_math_env,
    'align' : MathBlock.parse_math_env,
    'eqnarray' : MathBlock.parse_math_env,
    'multline' : MathBlock.parse_math_env,
    'alignat' : MathBlock.parse_math_env,
    'gather' : MathBlock.parse_math_env,
    'ensuremath' : MathBlock.parse_ensure_math,
    'empheq' : MathBlock.parse_math_env
}









