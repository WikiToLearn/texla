import logging
from . import utility
from . import CommandParser
from .Block import *

class LabelBlock(Block):
	'''Block that represents labels'''

	@staticmethod
	def parse_label(parser, tex, parent_block, params):
		options, left_tex = CommandParser.parse_options(
			tex, [('label','{','}')])
		label = options['label']
		logging.debug('LabelBlock.parse @ label: %s', label)
		block =  LabelBlock(label, parent_block)
		return (block, left_tex)

	def __init__(self, label, parent_block):
		super().__init__('label',label, parent_block)
		self.label = label 
		self.attributes['label'] = label

class RefBlock(Block):
	'''Block thar represents reference'''

	@staticmethod
	def parse_ref(parser, tex, parent_block, params):
		options, left_tex = CommandParser.parse_options(
			tex, [('ref','{','}')])
		ref = options['ref']
		ref_type = params['cmd']
		logging.debug('RefBlock.parse @ label: %s', ref)
		block = RefBlock(ref, ref_type, parent_block)
		return (block, left_tex)

	def __init__(self, ref, ref_type, parent_block):
		super().__init__(ref_type, ref, parent_block)
		self.ref = ref
		self.attributes['ref_type'] = ref_type
		self.attributes['ref'] = ref


parser_hooks = {
	'label' : LabelBlock.parse_label,
	'ref' : RefBlock.parse_ref,
	'vref' : RefBlock.parse_ref,
	'eqref' : RefBlock.parse_ref
}