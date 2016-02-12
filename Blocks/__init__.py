import os
import importlib


'''We can import here all the submodules and create the dictionary
of parser__hooks
'''
parser_hooks={}

for module in os.listdir("Blocks"):
    #utility module is not imported under Blocks
    if module == 'utility.py' or module =='__init__.py':
        continue
    if module.endswith('.py'):
        m = importlib.import_module('Blocks.'+ module[:-3])
        print(m)
        if hasattr(m,"parser_hooks"):
            for key,value  in m.parser_hooks().items():
                print(key,value)
                parser_hooks[key] = value
