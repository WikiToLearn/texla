import logging
import re


def check_space(block, text):
    #logging.debug("Plugin spaces_check @  checking output of block {}".
    #              format(block.id))
    r = re.compile(r'\n[ ]*')
    return r.sub("\n", text)


plugin_render_hooks = {
    'ALL' : {
        'post': check_space
    }
}
