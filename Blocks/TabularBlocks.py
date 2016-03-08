import logging
import re
from .Utilities import *
from .Block import Block

class TabularBlock(Block):

    @staticmethod
    def parse(parser, tex, parent_block, params):
        options, left_tex = CommandParser.parse_options(tex,
                [('pos','[',']'),('spec','{','}')])
        spec = TabularBlock.get_spec_dictionary(options['spec'])
        block = TabularBlock(options['pos'], spec, parent_block)
        block.table = []
        lines = tex.split('\\\\')
        for l in lines:
            columns = l.split('&')
            cols_list = []
            for c in columns:
                ch_blocks = parser.parse_instructions(c, block,{})
                cols_list.append(ch_blocks)
            block.table.append(cols_list)
        block.attributes['table'] = block.table
        return block

    @staticmethod
    def get_spec_dictionary(spec):
        '''
        This function create  a list for the spec of the tables
        '''
        spec_list = []
        i = 0
        while True:
            if i == len(spec):
                break
            ch = spec[i]
            if ch == '|':
                spec_list.append({'type' : 'separator',
                                  'sep' : 'vline'})
            elif ch == '@':
                r = re.match(r'{(.*?)}',spec[i+1:])
                m = r.group(1)
                i += (len(r.group()))
                spec_list.append({'type': 'separator',
                                  'sep': m})
            elif ch=='p':
                r = re.match(r'{(.*?)}', spec[i+1:])
                m = r.group(1)
                i += (len(r.group()))
                spec_list.append({'type': 'column',
                    'width': m})
            elif ch=='*':
                r = re.match(r'{(.*?)}{(.*?)}',spec[i+1:])
                N = int(r.group(1))
                typ = r.group(2)
                i += (len(r.group()))
                for j in range(N):
                    spec_list.append({'type':'column',
                                      'alignment':typ})
            else:
                spec_list.append({'type':'column',
                                  'alignment':ch})
            i+=1
        return spec_list


    def __init__(self, pos, spec, parent_block):
        super().__init__('tabular', '', parent_block)
        self.pos = pos
        self.attributes['pos'] = pos
        self.attributes['spec'] = spec


class HlineBlock(Block):

    def parse(parser, tex, parent_block, params):
        block = HlineBlock(parent_block)
        logging.debug('Hline.parse @ cmd: %s',
        			params['cmd'])
        return (block,tex)

    def __init__(self, parent_block):
        super().__init__('hline','',parent_block)



parser_hooks = {
    'tabular' : TabularBlock.parse,
    'hline' : HlineBlock.parse
}
