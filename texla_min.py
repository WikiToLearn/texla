import logging
import sys
import json

from texla.Parser import Parser
from texla.Renderers.MediaWikiRenderer import MediaWikiRenderer
import texla.PageTree.Exporter as exporter


def execute_texla_mediawiki(config):
    logging.info('######## STARTING PARSING ########')
    p = Parser(config)
    a = open(config['input_path'], 'r').read()
    tree = p.parse(a)
    n_blocks = tree.n_blocks()
    logging.info('PARSED %i Blocks', n_blocks)

    logging.info('######## STARTING RENDERING ########')
    #rendering
    rend = MediaWikiRenderer(config)
    rend.start_rendering(tree)

    #getting text of root_page
    output_text = rend.tree.root_page.text
    logging.info('######## STARTING EXPORTING ########')
    out = open(config['output_path'] + '.mw', 'w')
    out.write(output_text)
    logging.info('Finished')


if __name__ == '__main__':
    if len(sys.argv)<3:
        print("Insert the file_in and file_out!")
        exit()
    filein = sys.argv[1]
    fileout = sys.argv[2]
    config = {"input_path":filein,
              "output_path":fileout,
              "doc_title":"texla_min",
              "lang":"it",
              "keywords":{}
              }
    #reading JSON configs
    execute_texla_mediawiki(config)
