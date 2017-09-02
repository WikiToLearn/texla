import logging
import re
from ..Utilities import *
from .ReferenceBlocks import LabelBlock
from .Block import Block

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
        #creating and adding labels blocks
        for l in labels:
            lblock = LabelBlock(l, block)
            logging.debug('BLOCK @ %s%s',
                    "\t"*lblock.tree_depth, str(lblock))
            block.labels.append(lblock)
        return block

    @staticmethod
    def parse_ensure_math(parser, tex, parent_block, params):
        ''' The \ensuremath{} is a math command, not env'''
        options, left_tex = CommandParser.parse_options(tex,
            [('math','{','}')])
        text = options['math']
        block = MathBlock('ensuremath', False, text, parent_block)
        return (block, left_tex)

    @staticmethod
    def parse_empheq(parser, tex, parent_block, params):
        '''We need to extract the right environment from the options '''
        options, content = CommandParser.parse_options(tex,
                [("emph_opt","[","]"), ("env", "{","}")])
        env = options["env"]
        star = False
        if env.endswith("*"):
            env = env[:-1]
            star = True
        #getting labels and tex without labels
        tex, labels = MathBlock.parse_labels(content)
        #the content of the math is stripped
        block = MathBlock(env, star, tex.strip(), parent_block)
        #creating and adding labels blocks
        for l in labels:
            lblock = LabelBlock(l, block)
            logging.debug('BLOCK @ %s%s',
                    "\t"*lblock.tree_depth, str(lblock))
            block.labels.append(lblock)
        return block


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
        #list for labels blocks
        self.labels = []

    def __str__(self):
        return  '<Block:{}, ID:{}, math_type:{}, star:{}>'.format(
            self.block_name, self.id, self.attributes['math_type'],
            self.attributes['star'])


parser_hooks = {
    'inlinemath' : MathBlock.parse_math_env,
    'displaymath' : MathBlock.parse_math_env,
    'equation' : MathBlock.parse_math_env,
    'align' : MathBlock.parse_math_env,
    'eqnarray' : MathBlock.parse_math_env,
    'multline' : MathBlock.parse_math_env,
    'alignat' : MathBlock.parse_math_env,
    'gather' : MathBlock.parse_math_env,
    'ensuremath' : MathBlock.parse_ensure_math,
    'empheq' : MathBlock.parse_empheq,
    'math': MathBlock.parse_math_env
}
