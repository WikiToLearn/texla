import logging


def check_space(block, text):
    logging.debug("Plugin spaces_check @  checking output of block {}".
                  format(block.id))
    text = text.replace("\n ", "\n")
    return text


plugin_render_hooks = {
    'ALL' : {
        'post': check_space
    }
}
