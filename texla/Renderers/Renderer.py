from ..Parser import Blocks
import logging


class Renderer():
    def __init__(self):
        self.render_hooks = {}
        self.used_tags = {}

    def register_render_hooks(self, hooks):
        '''This function registers the hooks for renderer'''
        for key, item in hooks.items():
            self.render_hooks[key] = item

    def register_renderer_hook(self, name, hook):
        '''This function registers a hook for renderer'''
        self.render_hooks[name] = hook

    def render_children_blocks(self, block, collapse=True):
        output = []
        for bl in block.ch_blocks:
            #it's not necessary checking for renderer_hook
            #because default hook is mandatory
            output.append((bl.block_name, self.render_block(bl)))
        logging.debug('Render.ch_blocks @ %s', output)
        if collapse:
            return ''.join([x[1] for x in output])
        else:
            return output

    def render_block(self, bl):
        if bl.block_name in self.render_hooks:
            self.used_tag('ok      | ' + bl.block_name)
            logging.debug('Render @ block: ' + bl.block_name)
            return self.render_hooks[bl.block_name](bl)
        else:
            #default hook is mandatory
            self.used_tag('default | ' + bl.block_name)
            logging.debug('Render @ block: default@' + bl.block_name)
            return self.render_hooks['default'](bl)

    #Utils for debug
    def used_tag(self, tag):
        if tag in self.used_tags:
            self.used_tags[tag] += 1
        else:
            self.used_tags[tag] = 1
