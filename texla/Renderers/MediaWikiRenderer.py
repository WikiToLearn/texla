import logging
from .Renderer import Renderer
from ..PageTree.PageTree import *


class MediaWikiRenderer(Renderer):
    def __init__(self, configs):
        super().__init__()
        self.configs = {}
        self.doc_title = configs['doc_title']
        self.used_tag
        #register renderer_hook
        render_hooks = {
            #root
            'root-block': self.r_document,
            'default': self.default,
            #text
            'newpage': self.r_newpage,
            'newline': self.r_newline,
            '\\': self.r_newline,
            'text': self.r_text,
            'clearpage': self.r_newpage,
            'cleardoublepage': self.r_newpage,
            #formatting
            'centering': self.r_centering,
            'textbf': self.r_textbf,
            'textit': self.r_textit,
            'textsc': self.r_textsc,
            'textsuperscript': self.r_superscript,
            'textsubscript': self.r_subscript,
            '%': self.r_special_command,
            '&': self.r_special_command,
            '$': self.r_special_command,
            '{': self.r_special_command,
            '}': self.r_special_command,
            '#': self.r_special_command,
            '_': self.r_special_command,
            'dots': self.r_dots,
            'ldots': self.r_dots,
            'flushright': self.r_flushright,
            'flushleft': self.r_flushleft,
            'center': self.r_center,
            'abstract': self.r_abstract,
            'linebreak': self.r_break,
            'pagebreak': self.r_break,
            'nolinebreak': self.r_break,
            'nopagebreak': self.r_break,
            #sectioning
            'part': self.sectioning,
            'chapter': self.sectioning,
            'section': self.sectioning,
            'subsection': self.sectioning,
            'subsubsection': self.sectioning,
            'paragraph': self.sectioning,
            'subparagraph': self.sectioning,
            #lists
            'itemize': self.r_itemize,
            'enumerate': self.r_enumerate,
            'description': self.r_description,
            #quotes
            'quotation': self.r_quotes,
            'quote': self.r_quotes,
            'verse': self.r_verse,
            'footnote': self.r_footnote,
        }
        #registering the hooks
        self.register_render_hooks(render_hooks)
        #tree object
        self.tree = PageTree(configs)
        #parameter for list formatting
        self.list_level = ''
        #parameter for theorem handling
        self.in_theorem = False
        ####### TAGS ANALYSIS
        #dictionary for tag usage
        self.used_tags = {}

    def start_rendering(self, root_block):
        '''starting rendering from root-block'''
        self.render_block(root_block)
        #after rendering
        self.tree.after_render()

    #Utils for debug
    def used_tag(self, tag):
        if tag in self.used_tags:
            self.used_tags[tag] += 1
        else:
            self.used_tags[tag] = 1

    ####### ROOT BLOCK
    def r_document(self, block):
        self.used_tag('DOCUMENT')
        logging.info('Render @ block: ' + block.block_name)
        #we trigger the rendering of content
        text = self.render_children_blocks(block)
        #text is the tex outside sections
        self.tree.addText(text)

    ########################################
    #DEFAULT

    def default(self, block):
        #we don't print anything
        self.used_tag('DEFAULT@' + block.block_name)
        return ''

    #########################################
    #TEXT

    def r_text(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        return block.attributes['text']

    def r_newline(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        return '\n'

    def r_newpage(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        return '\n\n'

    #########################################
    #SECTIONING

    def sectioning(self, block):
        title = block.attributes['title']
        section_name = block.attributes['section_name']
        #remove the \n insiede title
        title = re.sub('\\n*', '', title)
        #creation of the new page
        self.tree.createPage(title, section_name)
        #content processing
        text = self.render_children_blocks(block)
        #adding text to current page
        self.tree.addText(text)
        #exiting the section
        self.tree.exitPage()
        return ''

    #########################################
    #FORMATTING

    def r_special_command(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        return block.attributes['character']

    def r_dots(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        return '...'

    def r_textbf(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        s = []
        s.append("\'\'\'")
        s.append(self.render_children_blocks(block))
        s.append("\'\'\'")
        return ''.join(s)

    def r_textit(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        s = []
        s.append("\'\'")
        s.append(self.render_children_blocks(block))
        s.append("\'\'")
        return ''.join(s)

    def r_textsc(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        return self.render_children_blocks(block).upper()

    def r_superscript(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        s = []
        s.append('<sup>')
        s.append(self.render_children_blocks(block))
        s.append('</sup>')
        return ''.join(s)

    def r_subscript(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        s = []
        s.append('<sub>')
        s.append(self.render_children_blocks(block))
        s.append('</sub>')
        return ''.join(s)

    def r_abstract(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        s = []
        s.append('{{abstract|')
        s.append(self.render_children_blocks(block))
        s.append('}}')
        return ''.join(s)

    def r_break(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        return ''

    #########################################
    #ALIGNMENT

    def r_center(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        s = []
        s.append('{{center|')
        s.append(self.render_children_blocks(block))
        s.append('}}')
        return ''.join(s)

    def r_centering(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        s = []
        s.append('(')
        s.append(self.render_children_blocks(block))
        s.append(')')
        return ''.join(s)

    def r_flushleft(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        s = []
        s.append('{{left|')
        s.append(self.render_children_blocks(block))
        s.append('}}')
        return ''.join(s)

    def r_flushright(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        s = []
        s.append('{{right|')
        s.append(self.render_children_blocks(block))
        s.append('}}')
        return ''.join(s)

    #########################################
    #LISTS

    def r_itemize(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        self.list_level += '*'
        s = []
        for item in block.ch_blocks:
            s.append(self.list_level)
            s.append(self.render_children_blocks(item))
            s.append("\n")
        self.list_level = self.list_level[:-1]
        return ''.join(s)

    def r_enumerate(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        self.list_level += '#'
        s = []
        for item in block.ch_blocks:
            s.append(self.list_level)
            s.append(self.render_children_blocks(item))
            s.append("\n")
        self.list_level = self.list_level[:-1]
        return ''.join(s)

    def r_description(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        s = []
        for item in block.ch_blocks:
            s.append(';')
            s.append(item.attributes['word'])
            s.append(':')
            s.append(self.render_children_blocks(item))
            s.append("\n")
        return ''.join(s)

    #########################################
    #QUOTES

    def r_quotes(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        s = []
        s.append('<blockquote>')
        s.append(self.render_children_blocks(block))
        s.append('</blockquote>')
        return ''.join(s)

    def r_verse(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        s = []
        s.append('<blockquote>')
        s.append('\n'.join(self.render_children_blocks(block).split('//')))
        s.append('</blockquote>')
        return ''.join(s)

    def r_footnote(self, block):
        self.used_tag(block.block_name)
        logging.info('Render @ block: ' + block.block_name)
        s = []
        s.append("<ref>")
        s.append(self.render_children_blocks(block))
        s.append("</ref>")
        return ''.join(s)
