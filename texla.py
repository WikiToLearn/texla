import logging
import sys

loglevel = sys.argv[1].split('=')[1]
if len(sys.argv)>2:
	output =  sys.argv[2].split('=')[1] in ('True','true','Y','y','yes','Yes')
else:
	output = False

numeric_level = getattr(logging, loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % loglevel)

if output:
	logging.basicConfig(filename='tree.log',
		format='%(levelname)s:%(message)s',
		level=numeric_level)
else:
	logging.basicConfig(
		format='%(levelname)s:%(message)s',
		level=numeric_level)
logging.info('Started')

from texla.Parser import Parser
from texla.Renderers.MediaWikiRenderer import MediaWikiRenderer

p = Parser()
a = open('test.tex','r').read()
tree = p.parse(a)
f = open('tree','w')
json = tree.to_json(0)
f.write(json)

logging.info('########STARTING RENDERING########')

#rendering
rend = MediaWikiRenderer({'doc_title':'Prova','output_path':"test.mw",
                        'keywords':'', 'base_path':''})
rend.start_rendering(tree)

o = open('output.mw','w')
o.write(rend.tree.get_tree_json())
logging.info('Finished')
