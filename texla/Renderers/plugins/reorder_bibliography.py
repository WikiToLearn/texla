import re
from ..utils import *
import logging

cit_order = []
bib_block = None

def save_cite(block):
    global cit_order
    cit_order += block.attributes["labels"]

def save_biblio(block):
    global bib_block
    bib_block = block

def print_biblio():
    print(len(cit_order))
    with open(configs["output_path"], "w") as f:
        opts = bib_block.attributes["options"]
        f.write(f"\\begin{{thebibliography}}{{{opts}}}\n")
        written_items = []
        for c in cit_order:
            if c not in written_items:
                logging.info(f"Printing bibitem {c}")
                f.write(f'\\bibitem{{{c}}}\n{bib_block.items[c].get_content_children()}\n\n')
                written_items.append(c)
        f.write("\\end{thebibliography}")

plugin_render_hooks = {
    'cite' : { "pre": save_cite },
    'thebibliography' : { "pre": save_biblio }
}
plugin_lifecycle_hooks = {"end": print_biblio }