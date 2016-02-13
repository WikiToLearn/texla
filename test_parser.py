import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
logging.info('Started')
    
from Parser import Parser

p = Parser() 
a = open('tests/test_sections.tex','r').read()
result = p.parse(a)
json = result[0].to_json(0)
open('tree','w').write(json)

logging.info('Finished')