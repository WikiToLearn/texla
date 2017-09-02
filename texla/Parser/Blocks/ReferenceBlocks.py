import logging
from ..Utilities import *
from .Block import Block

class LabelBlock(Block):
    '''Block that represents labels'''

    @staticmethod
    def parse_label(parser, tex, parent_block, params):
        options, left_tex = CommandParser.parse_options(
            tex, [('label','{','}')])
        label = options['label']
        block =  LabelBlock(label, parent_block)
        return (block, left_tex)

    def __init__(self, label, parent_block):
        super().__init__('label',label, parent_block)
        self.label = label
        self.attributes['label'] = label

    def __str__(self):
        return '<Block:{}, ID:{}, label:{}>'.format(
             self.block_name, self.id, self.label)

class RefBlock(Block):
    '''Block thar represents reference'''

    @staticmethod
    def parse_ref(parser, tex, parent_block, params):
        options, left_tex = CommandParser.parse_options(
            tex, [('ref','{','}')])
        ref = options['ref']
        ref_type = params['cmd']
        block = RefBlock(ref, ref_type, parent_block)
        return (block, left_tex)

    def __init__(self, ref, ref_type, parent_block):
        super().__init__(ref_type, ref, parent_block)
        self.ref = ref
        self.ref_type = ref_type
        self.attributes['ref_type'] = ref_type
        self.attributes['ref'] = ref

    def __str__(self):
        return '<Block:{}, ID:{}, label:{}>'.format(
             self.block_name, self.id, self.ref)


parser_hooks = {
    'label' : LabelBlock.parse_label,
    'ref' : RefBlock.parse_ref,
    'vref' : RefBlock.parse_ref,
    'eqref' : RefBlock.parse_ref
}
