import logging
from . import utility
from . import CommandParser
from .Block import *

class MathBlock(Block):

    @staticmethod
    def parse_math_env(parser, tex, parent_block, options):
        ''' This parse hook it's used for $$, $, \[ \( and
        general math environments'''
        env = options['env']
        star = options.get('star',False)
        #the content of the math is stripped
        block = MathBlock(env, star, tex.strip(), parent_block)
        logging.debug('MathBlock.parse_math_env @ env: %s', env)
        return block

    @staticmethod
    def parse_ensure_math(parser, tex, parent_block, options):
        ''' The \ensuremath{} is a math command, not env'''
        param, left_tex = CommandParser.parse_options(tex,
            [('math','{','}')])
        text = param['math']
        block = MathBlock('ensuremath', False, text, parent_block)
        logging.debug('MathBlock.parse_ensure_math')
        return (block, left_tex)


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
    'ensuremath' : MathBlock.parse_ensure_math
}









