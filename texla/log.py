import logging
import sys

if len(sys.argv) > 1:
    loglevelstr = sys.argv[1][2:]
    if loglevelstr in ["info", "debug", "error", "warn"]:
        loglevel = loglevelstr
    else:
        loglevel = "info"
else:
    loglevel = "info"

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
