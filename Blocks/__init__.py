import os
import importlib
import logging


'''We can import here all the submodules and create the dictionary
of parser__hooks
'''
parser_hooks={}

not_import = ('__init__.py', 'utility.py', 'DocumentBlock.py',
    'CommandParser.py', 'MacroParser.py')

for module in os.listdir("Blocks"):
    #utility module is not imported under Blocks
    if module in not_import:
        continue
    if module.endswith('.py'):
        m = importlib.import_module('Blocks.'+ module[:-3])
        logging.info('BLOCKS_MODULE @ imported %s', m.__name__)
        if hasattr(m,"parser_hooks"):
            for key,value  in m.parser_hooks.items():
                logging.info('BLOCKS_HOOK @ parser_hook: %s | %s', key, value)
                parser_hooks[key] = value
logging.info('Supported commands/environments:\n%s',
    '\n'.join(['@ '+key for key in sorted(parser_hooks.keys())]))
