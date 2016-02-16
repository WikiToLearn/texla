import logging
from . import utility
from . import CommandParser
from .Block import *

class AlignmentBlock(Block):
	'''This class handles the flushright, flushleft
	and center environments'''

	@staticmethod
	def parse(parser, tex, parent_block, options):
		#we first create the Block
		block = AlignmentBlock(options['env'], tex, parent_block)
		logging.debug('AlignmentBlock.parse @ type: %s', options['env'])
		#now we parse the content 
		poptions = {'parse_sections':False,
                   'parse_envs':True,
                   'parse_math':True,
                   'parse_commands':True }
		children_blocks = parser.parser_cycle(tex, block, poptions)
		#now we can add the children nodes
		block.add_children_blocks(children_blocks)
		return block


	def __init__(self, align_type, tex, parent_block):
		super().__init__(align_type, tex, parent_block)
		self.attributes['align_type'] = align_type

	def __str__(self):
		return '<Block:{}, ID:{}, alignment:{}>'.format( 
			self.block_name, self.id, self.attributes['align_type'])


parser_hooks = {
	'flushleft' : AlignmentBlock.parse,
	'flushright' : AlignmentBlock.parse,
	'center' : AlignmentBlock.parse
}


