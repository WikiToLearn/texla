import logging
from .Renderer import Renderer
from ..PageTree.PageTree import *
from . import MathCheck

class MediaWikiRenderer(Renderer):

    def __init__(self, configs):
        super().__init__()
        self.configs = configs
        self.doc_title = configs['doc_title']
        #registering the hooks
        self.register_render_hooks(self.get_render_hooks())
        #tree object
        self.tree = PageTree(configs)
        #parameter for list formatting
        self.list_level = ''
        #parameters for theorem handling
        self.in_theorem = False
        self.th_numbering = {}

    ########################################
    #STARTING POINT

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
        #rendering labels
        self.render_blocks(block.labels)
        return '<dmath>' + s + '</dmath>'

    def r_inline_math(self, block):
        s = block.attributes['content']
        #check math content
        s = MathCheck.math_check(s)
        #rendering labels
        self.render_blocks(block.labels)
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
        #rendering labels
        self.render_blocks(block.labels)
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

    def r_special_character(self, block):
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

    def r_underline(self, block):
        s = []
        s.append('{{Sottolineato|')
        s.append(self.render_children_blocks(block))
        s.append('}}')
        return ''.join(s)

    def r_abstract(self, block):
        s = []
        s.append('{{Abstract|')
        s.append(self.render_children_blocks(block))
        s.append('}}')
        return ''.join(s)

    def r_break(self, block):
        return ''

    def r_vspace(self,block):
        return '\n\n'

    def r_mandatory_space(self,block):
        return ' '

    def r_verbatim(self, block):
        return '<pre>' + block.attributes['content'] +'</pre>'

    def r_verb(self, block):
        return '<tt>' + block.attributes['content'] +'</tt>'

    #########################################
    #ALIGNMENT

    def r_center(self, block):
        s = []
        s.append('{{Center|')
        s.append(self.render_children_blocks(block))
        s.append('}}')
        return ''.join(s)

    def r_flushleft(self, block):
        s = []
        s.append('{{Flushleft|')
        s.append(self.render_children_blocks(block))
        s.append('}}')
        return ''.join(s)

    def r_flushright(self, block):
        s = []
        s.append('{{Flushright|')
        s.append(self.render_children_blocks(block))
        s.append('}}')
        return ''.join(s)

    #########################################
    #LISTS

    def r_itemize(self, block):
        self.list_level += '*'
        s = ['\n']
        for item in block.ch_blocks:
            s.append(self.list_level)
            s.append(self.render_children_blocks(item))
            s.append("\n")
        self.list_level = self.list_level[:-1]
        return ''.join(s)

    def r_enumerate(self, block):
        self.list_level += '#'
        s = ['\n']
        for item in block.ch_blocks:
            s.append(self.list_level)
            s.append(self.render_children_blocks(item))
            s.append("\n")
        self.list_level = self.list_level[:-1]
        return ''.join(s)

    def r_description(self, block):
        s = ['\n']
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

    #########################################
    #Theorems

    def r_theorem(self, block):
        #the label in theorems is not working for now
        th_definition = block.attributes['definition']
        th_title = ''
        if not block.attributes['star']:
            counter = block.attributes['counter']
            if counter==None:
                counter = block.th_type
            if counter in self.th_numbering:
                num = self.th_numbering[counter] +1
            else:
                num = 1
            th_title += str(num)
            self.th_numbering[counter] = num
        if block.attributes['title'] != None:
            th_title +=" "+ block.attributes['title']
        s = ['\n']
        if self.configs['lang'] =='it':
            if th_definition.lower() == 'teorema':
            #adding content to page through a template
                s.append("\n{{Teorema|titolo=" + \
                        th_title+"|")
            elif th_definition.lower() == 'definizione':
                s.append("\n{{Definizione|titolo=" + \
                        th_title+"|")
            elif th_definition.lower() == 'proposizione':
                s.append("\n{{Proposizione|titolo=" + \
                        th_title+"|")
            elif th_definition.lower() == 'lemma':
                s.append("\n{{Lemma|title=" + \
                        th_title+"|")
            elif th_definition.lower() == 'corollario':
                s.append("\n{{Corollario|titolo=" + \
                        th_title+"|")
            elif th_definition.lower()[:-2] == 'eserciz':
                s.append("\n{{Esercizio|titolo=" + \
                        th_title+"|")
            elif th_definition.lower()[:-1] == 'osservazion':
                s.append("\n{{Osservazione|titolo=" + \
                        th_title+"|")
            elif th_definition.lower()[:-2] == 'esemp':
                s.append("\n{{Esempio|titolo=" + \
                        th_title+"|")
            elif th_definition.lower() == 'dimostrazione':
                s.append("\n{{Dimostrazione|titolo=" + \
                        th_title+"|")
            else:
                s.append("\n{{Environment|name="+ th_definition + \
                        "|title=" + th_title +\
                        "|content=")
        elif self.configs['lang'] =='en':
            if th_definition.lower() == 'theorem':
            #adding content to page through a template
                s.append("\n{{Theorem|title=" + \
                        th_title+"|")
            elif th_definition.lower() == 'definition':
                s.append("\n{{Definition|title=" + \
                        th_title+"|")
            elif th_definition.lower() == 'proposition':
                s.append("\n{{Proposition|title=" + \
                        th_title+"|")
            elif th_definition.lower() == 'lemma':
                s.append("\n{{Lemma|title=" + \
                        th_title+"|")
            elif th_definition.lower() == 'corollarium':
                s.append("\n{{Corollarium|title=" + \
                        th_title+"|")
            elif th_definition.lower() == 'exercise':
                s.append("\n{{Exercise|title=" + \
                        th_title+"|")
            elif th_definition.lower() == 'observation':
                s.append("\n{{Observation|title=" + \
                        th_title+"|")
            elif th_definition.lower() == 'remark':
                s.append("\n{{Remark|title=" + \
                        th_title+"|")
            elif th_definition.lower() == 'example':
                s.append("\n{{Example|title=" + \
                        th_title+"|")
            elif th_definition.lower() == 'demonstration':
                s.append("\n{{Demonstration|title=" + \
                        th_title+"|")
            else:
                s.append("\n{{Environment|name="+ th_definition + \
                        "|title=" + th_title +\
                        "|content=")
        #insertig theorem content
        s.append(self.render_children_blocks(block))
        s.append('}}\n')
        return '\n'.join(s)

    def r_proof(self, block):
        s=[]
        if self.configs['lang'] == 'it':
            if block.title !=None:
                s.append('\n{{Dimostrazione|titolo='+\
                        block.attributes['title'])
            else:
                s.append('\n{{Dimostrazione|')
        elif self.configs['lang'] == 'en':
            if block.title !=None:
                s.append('\n{{Proof|title='+\
                        block.attributes['title'])
            else:
                s.append('\n{{Proof|')
        s.append(self.render_children_blocks(block))
        s.append('}}\n')
        return '\n'.join(s)



    def get_render_hooks(self):
        '''Render hooks'''
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
            'textbf': self.r_textbf,
            'textit': self.r_textit,
            'textsc': self.r_textsc,
            'textsuperscript': self.r_superscript,
            'textsubscript': self.r_subscript,
            'underline': self.r_underline,
            'uline': self.r_underline,
            '%': self.r_special_character,
            '&': self.r_special_character,
            '$': self.r_special_character,
            '{': self.r_special_character,
            '}': self.r_special_character,
            '#': self.r_special_character,
            '_': self.r_special_character,
            'dots': self.r_dots,
            'ldots': self.r_dots,
            'flushright': self.r_flushright,
            'flushleft': self.r_flushleft,
            'center': self.r_center,
            'centerline': self.r_center,
            'abstract': self.r_abstract,
            'linebreak': self.r_break,
            'pagebreak': self.r_break,
            'nolinebreak': self.r_break,
            'nopagebreak': self.r_break,
            'verbatim': self.r_verbatim,
            'verb': self.r_verb,
            #spaces
            'vspace': self.r_vspace,
            'mandatory_space': self.r_mandatory_space,
            #theorems
            'theorem' : self.r_theorem,
            'proof' : self.r_proof,
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
            'inlinemath': self.r_inline_math,
            'ensuremath': self.r_inline_math,
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
        return render_hooks
