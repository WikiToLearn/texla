from ..Parser import Blocks
import logging
import importlib

class Renderer():
    def __init__(self):
        self.render_hooks = {}
        self.pre_render_hooks = {}
        self.post_render_hooks = {}
        self.loaded_plugins = {}
        self.used_tags = {}

    def register_plugins(self, plugins):
        for plugin in plugins:
            m = importlib.import_module("..plugins"+'.'+ plugin, __name__)
            if hasattr(m, "plugin_hooks"):
                self.loaded_plugins[plugin] = m.plugin_hooks
                self.register_render_plugin_hooks(m.plugin_hooks)
                logging.info("Renderer.register_plugins "\
                             "@ Loaded plugin: {}".format(plugin))
                logging.info("Plugin {} hooks: {}".format( plugin,
                            list(m.plugin_hooks.keys())))


    def register_render_plugin_hooks(self, hooks):
        '''This function registers the hooks for renderer plugins.
        The plugins can define hooks for pre and post render actions.
        The pre hook receives the block before the rendering and can
        only return the block itself, modified.
        The post hook receive the block and the text from the renderer:
        it has to return the final text only.'''
        for bl in hooks:
            if "pre" in hooks[bl]:
                self.register_pre_renderer_hook(bl, hooks[bl]["pre"])
            if "post" in hooks[bl]:
                self.register_pre_renderer_hook(bl, hooks[bl]["post"])

    def register_pre_renderer_hook(self, block, hook):
        if block not in self.pre_render_hooks:
            self.pre_render_hooks[block] = []
        self.pre_render_hooks[block].append(hook)

    def register_post_renderer_hook(self, block, hook):
        if block not in self.post_render_hooks:
            self.post_render_hooks[block] = []
        self.post_render_hooks[block].append(hook)

    def render_children_blocks(self, block, collapse=True):
        '''This is one of the most important funciont
        of the rendering process.
        This function takes all the children blocks of
        a block and get they rendering output.
        If collapsed=True it returns a unique string,
        otherwise it returns a list of tuples with[(block_name, output)]
        '''
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
        '''This function calls the right render_hook for
        the block. If there isn't an hook it calld the default,
        that is mandatory'''
        output = ""
        ######### pre hooks ############
        #hooks executed in the order of inserction
        #They receive the block and they can only modify the block object
        if bl.block_name in self.pre_render_hooks:
            for prehook in self.pre_render_hooks[bl.block_name]:
                #calling prehook with the block
                prehook(bl)
        ######## rendering #############
        if bl.block_name in self.render_hooks:
            self.used_tag('ok      | ' + bl.block_name)
            logging.debug('Render @ block: ' + bl.block_name)
            output = self.render_hooks[bl.block_name](bl)
        else:
            #default hook is mandatory
            self.used_tag('default | ' + bl.block_name)
            logging.debug('Render @ block: default@' + bl.block_name)
            output = self.render_hooks['default'](bl)
        ######## post hooks ###########
        #hooks executed in the order of inserction.
        #They receive the block and text. They have to return the
        #output text, that is passed to the next posthook
        if bl.block_name in self.post_render_hooks:
            for posthook in self.post_render_hooks[bl.block_name]:
                #calling posthook with the block and output
                output = postblos(bl, output)
        #final output
        return output


    def render_blocks(self, bls, collapse=False):
        '''This function renderes a list of blocks.
        It's the same as render_children_blocks but
        with a generic list'''
        output = []
        for bl in bls:
            output.append((bl.block_name,self.render_block(bl)))
        if collapse:
            return ''.join([x[1] for x in output])
        else:
            return output

    #Utils for debug
    def used_tag(self, tag):
        if tag in self.used_tags:
            self.used_tags[tag] += 1
        else:
            self.used_tags[tag] = 1
