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
logging.info('texla started')
