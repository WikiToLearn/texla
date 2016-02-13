import logging
import sys

loglevel = sys.argv[1].split('=')[1]

numeric_level = getattr(logging, loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % loglevel)


logging.basicConfig(format='%(levelname)s:%(message)s', level=numeric_level)
logging.info('Started')
    
from Parser import Parser

p = Parser() 
a = open('tests/test_sections.tex','r').read()
result = p.parse(a)
json = result[0].to_json(0)
open('tree','w').write(json)

logging.info('Finished')