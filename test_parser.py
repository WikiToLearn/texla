import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
logging.info('Started')
    
from Parser import Parser



p = Parser() 
a = open('tests/test2.tex','r').read()
p.parse(a)


logging.info('Finished')