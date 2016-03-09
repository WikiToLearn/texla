from . import Blocks
import logging

class Renderer():

    def __init__(self):
        self.render_hooks = {}

    def register_render_hooks(self, hooks):
        '''This function registers the hooks for renderer'''
        for key, item in hooks.items():
            self.render_hooks[key] = item

    def register_renderer_hook(self, name, hook):
        '''This function registers a hook for renderer'''
        self.render_hooks[name] = hook

    def render_children_blocks(self, block, collapse=False):
        output = []
        for bl in block.ch_blocks:
            #searching for renderer_hook
            if bl.block_name in self.render_hooks:
                loggin
                output.append((bl.block_name,
                       self.render_hooks[bl.block_name](bl)))
            else:
                #default hook is mandatory
                output.append((bl.block_name,
                       self.render_hooks['default'](bl)))
        if collapse:
            return ''.join([x[1] for x in l])
        else:
            return output

    def render_block(self, bl):
        if bl.block_name in self.render_hooks:
            return self.render_hooks[bl.block_name](bl)
        else:
            #default hook is mandatory
            return self.render_hooks['default'](bl)
