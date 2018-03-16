import re
from ..utils import *
import logging

cit_order = []
bibliography_items = {}

def save_cite(block):
    cit_order.append(block.attributes["label"])

def save_biblio(block):
    global bibliography_items
    bibliography_items = block.items
    print(bibliography_items)

def print_biblio():
    with open(configs["output_path"], "w") as f:
        written_items = []
        for c in cit_order:
            if c not in written_items:
                f.write(f'\\bibitem{{{c}}}\n{bibliography_items[c].get_content_children()}\n\n')
                written_items.append(c)

plugin_render_hooks = {
    'cite' : { "pre": save_cite },
    'thebibliography' : { "pre": save_biblio }
}
plugin_lifecycle_hooks = {"end": print_biblio }