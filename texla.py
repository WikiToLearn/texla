import logging
import sys
import json
import log

from texla.Parser import Parser
from texla.Renderers.MediaWikiRenderer import MediaWikiRenderer
import texla.PageTree.Exporter as exporter


def execute_texla_mediawiki(config):
    logging.info('######## STARTING PARSING ########')
    p = Parser()
    a = open(config['input_path'], 'r').read()
    tree = p.parse(a)
    f = open(config['output_path'] + '.tree', 'w')
    json_tree = tree.to_json(0)
    n_blocks = tree.n_blocks()
    logging.info('PARSED %i Blocks', n_blocks)
    f.write(json_tree)
    logging.info('######## STARTING RENDERING ########')
    #rendering
    rend = MediaWikiRenderer(config)
    rend.start_rendering(tree)
    o = open(config['output_path'] + '.json', 'w')
    o.write(json.dumps(rend.tree.get_tree_json(), indent=3))
    p = open(config['output_path'] + '.debug', 'w')
    p.write(json.dumps(rend.used_tags, indent=2))
    #collpasing
    logging.info('######## STARTING POST-PROCESSING ########')
    tree = rend.tree
    tree.collapseSubpages_level(config['collapse_level'])
    tree.collapseURLs()
    logging.info('######## STARTING EXPORTING ########')
    if config['create_index']:
        tree.createIndex()
    exporter.exportPages(tree.pages, config['output_path'] + '.mw',
                         config['export_format'])
    if config['export_single_pages']:
        exporter.export_singlePages(tree.pages,
                                    config['output_path'] + '_pages',
                                    config['export_format'])
    logging.info('Finished')


if __name__ == '__main__':
    #reading JSON configs
    p = json.loads(open('configs.txt').read())
    config = p
    config['collapse_level'] = int(p['collapse_level'])
    config['export_single_pages'] = bool(int(p['export_single_pages']))
    config['create_index'] = bool(int(p['create_index']))
    config['print_preparsed_tex'] = bool(int(p['print_preparsed_tex']))
    #loading localized keywords
    config['keywords'] = json.loads(open('lang.txt').read())[config['lang']]
    #executing process for alla renderers
    if config['renderer'] == 'mediawiki':
        execute_texla_mediawiki(config)
