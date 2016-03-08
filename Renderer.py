import Blocks

class Renderer():

    def __init__():
        self.renderer_hooks = {}

    def register_renderer_hooks(self, hooks):
        '''This function registers the hooks for renderer'''
        self.render_hooks = hooks

    def render_children_blocks(self, block, collapse=False):
        output = []
        for bl in block.ch_blocks:
            #searching for renderer_hook
            if bl.block_name in renderer_hooks:
                output.append((bl.block_name,
                               renderer_hooks[bl.block_name](bl)))
            else:
                #default hook is mandatory
                output.append((bl.block_name),
                              renderer_hooks['default'](bl)))
        if collapse:
            return ''.join([x[1] for x in l])
        else:
            return output
