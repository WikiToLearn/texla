import os
import importlib
import logging


'''We can import here all the submodules and create the dictionary
of parser__hooks
'''
parser_hooks={}

not_import = ('__init__.py', 'utility.py', 'DocumentBlock.py',
              'CommandParser.py','EnvironmentParser.py', 'MacroParser.py')

#getting path of the modules
for module in os.listdir(os.path.dirname(__file__)):
    #utility module is not imported under Blocks
    if module in not_import:
        continue
    if module.endswith('.py'):
        m = importlib.import_module(__name__+'.'+ module[:-3])
        logging.debug('BLOCKS_MODULE @ imported %s', m.__name__)
        if hasattr(m,"parser_hooks"):
            for key,value  in m.parser_hooks.items():
                logging.debug('BLOCKS_HOOK @ parser_hook: %s | %s', key, value)
                parser_hooks[key] = value
logging.debug('Supported commands/environments:\n%s',
    '\n'.join(['@ '+key for key in sorted(parser_hooks.keys())]))
