import logging
from .Renderer import Renderer
from ..PageTree.PageTree import *
from . import MathCheck


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
            'par': self.r_par,
            'newpage': self.r_newpage,
            'newline': self.r_newline,
            '\\': self.r_newline,
            'text': self.r_text,
            'clearpage': self.r_newpage,
            'cleardoublepage': self.r_newpage,
            #formatting
            'emph': self.r_textit,
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
            #math
            'displaymath': self.r_display_math,
            'equation': self.r_display_math,
            'eqnarray': self.r_align,
            'multline': self.r_align,
            'alignat': self.r_align,
            #lists
            'itemize': self.r_itemize,
            'enumerate': self.r_enumerate,
            'description': self.r_description,
            #quotes
            'quotation': self.r_quotes,
            'quote': self.r_quotes,
            'verse': self.r_verse,
            'footnote': self.r_footnote,
            #labels
            'label': self.r_label,
            'ref': self.r_ref,
            'vref': self.r_ref,
            'pageref': self.r_ref,
            'eqref': self.r_ref
        }
        #registering the hooks
        self.register_render_hooks(render_hooks)
        #tree object
        self.tree = PageTree(configs)
        #parameter for list formatting
        self.list_level = ''
        #parameter for theorem handling
        self.in_theorem = False

    def start_rendering(self, root_block):
        '''starting rendering from root-block'''
        self.render_block(root_block)
        #after rendering
        self.tree.after_render()

    ####### ROOT BLOCK
    def r_document(self, block):
        #we trigger the rendering of content
        text = self.render_children_blocks(block)
        #text is the tex outside sections
        self.tree.addText(text)

    ########################################
    #DEFAULT

    def default(self, block):
        #we don't print anything
        return ''

    #########################################
    #TEXT

    def r_text(self, block):
        text = block.attributes['text']
        return text

    def r_newline(self, block):
        return '\n'

    def r_newpage(self, block):
        return '\n\n'

    def r_par(self, block):
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
    #MATH

    def r_display_math(self, block):
        s = block.attributes['content']
        #check math content
        s = MathCheck.math_check(s)
        return '<dmath>' + s + '</dmath>'

    def r_inline_math(self, block):
        s = block.attributes['content']
        #check math content
        s = MathCheck.math_check(s)
        return '<math>' + s + '</math>'

    def r_align(self, block):
        s = block.attributes['content']
        s = s.replace('alignat', 'align')
        s = s.replace('eqnarray', 'align')
        s = s.replace('multline', 'align')
        s = s.replace('align*', 'align')
        s = s.replace('alignat*', 'align')
        s = s.replace('eqnarray*', 'align')
        s = s.replace('multline*', 'align')
        #check math content
        s = MathCheck.math_check(s)
        return '<dmath type=align>' + s + '</dmath>'

    #########################################
    #LABELS and refs

    def r_label(self, block):
        label = block.attributes['label']
        self.tree.addLabel(label)
        return ''

    def r_ref(self, block):
        ref = block.attributes['ref']
        return '\\ref{' + ref + '}'

    #########################################
    #FORMATTING

    def r_special_command(self, block):
        return block.attributes['character']

    def r_dots(self, block):
        return '...'

    def r_textbf(self, block):
        s = []
        s.append("\'\'\'")
        s.append(self.render_children_blocks(block))
        s.append("\'\'\'")
        return ''.join(s)

    def r_textit(self, block):
        s = []
        s.append("\'\'")
        s.append(self.render_children_blocks(block))
        s.append("\'\'")
        return ''.join(s)

    def r_textsc(self, block):
        return self.render_children_blocks(block).upper()

    def r_superscript(self, block):
        s = []
        s.append('<sup>')
        s.append(self.render_children_blocks(block))
        s.append('</sup>')
        return ''.join(s)

    def r_subscript(self, block):
        s = []
        s.append('<sub>')
        s.append(self.render_children_blocks(block))
        s.append('</sub>')
        return ''.join(s)

    def r_abstract(self, block):
        s = []
        s.append('{{abstract|')
        s.append(self.render_children_blocks(block))
        s.append('}}')
        return ''.join(s)

    def r_break(self, block):
        return ''

    #########################################
    #ALIGNMENT

    def r_center(self, block):
        s = []
        s.append('{{center|')
        s.append(self.render_children_blocks(block))
        s.append('}}')
        return ''.join(s)

    def r_centering(self, block):
        s = []
        s.append('{{center')
        s.append(self.render_children_blocks(block))
        s.append('}}')
        return ''.join(s)

    def r_flushleft(self, block):
        s = []
        s.append('{{left|')
        s.append(self.render_children_blocks(block))
        s.append('}}')
        return ''.join(s)

    def r_flushright(self, block):
        s = []
        s.append('{{right|')
        s.append(self.render_children_blocks(block))
        s.append('}}')
        return ''.join(s)

    #########################################
    #LISTS

    def r_itemize(self, block):
        self.list_level += '*'
        s = []
        for item in block.ch_blocks:
            s.append(self.list_level)
            s.append(self.render_children_blocks(item))
            s.append("\n")
        self.list_level = self.list_level[:-1]
        return ''.join(s)

    def r_enumerate(self, block):
        self.list_level += '#'
        s = []
        for item in block.ch_blocks:
            s.append(self.list_level)
            s.append(self.render_children_blocks(item))
            s.append("\n")
        self.list_level = self.list_level[:-1]
        return ''.join(s)

    def r_description(self, block):
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
        s = []
        s.append('<blockquote>')
        s.append(self.render_children_blocks(block))
        s.append('</blockquote>')
        return ''.join(s)

    def r_verse(self, block):
        s = []
        s.append('<blockquote>')
        s.append('\n'.join(self.render_children_blocks(block).split('//')))
        s.append('</blockquote>')
        return ''.join(s)

    def r_footnote(self, block):
        s = []
        s.append("<ref>")
        s.append(self.render_children_blocks(block))
        s.append("</ref>")
        return ''.join(s)
