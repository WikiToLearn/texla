import logging
from .Renderer import Renderer
from ..PageTree.PageTree import *

class MediaWikiRenderer(Renderer):

    def __init__(self, configs, reporter):
        super().__init__(configs, reporter)
        self.configs = configs
        self.doc_title = configs['doc_title']
        #saving the hooks
        self.render_hooks = {
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
            'align': self.r_align,
            'alignat': self.r_align,
            'gather': self.r_gather,
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
            'eqref': self.r_ref,
            #accents
            "accented_letter": self.r_accented_letter,
            #figures
            "figure": self.r_figure
            }
        #tree object
        self.tree = PageTree(configs)
        #parameter for list formatting
        self.list_level = ''
        #parameters for theorem handling
        self.in_theorem = False
        self.theorem_number = 0
        self.th_numbering = {}

    ########################################
    #STARTING POINT

    def start_rendering(self, root_block):
        """starting rendering from root-block"""
        #start rendering of base class
        super(MediaWikiRenderer, self).start_rendering(root_block)
        self.render_block(root_block)
        #after rendering
        self.tree.after_render()
        #end rendering of base class
        super(MediaWikiRenderer, self).end_rendering()

    ####### ROOT BLOCK
    def r_document(self, block):
        #we trigger the rendering of content
        text = self.render_children_blocks(block)
        #text is the tex outside sections
        self.tree.addText(text)
        #returning the text to respect the interface
        return text

    ########################################
    #DEFAULT

    def default(self, block):
        #we don't print anything
        return ''

    #########################################
    #TEXT

    def r_text(self, block):
        text = block.attributes['text']

        # The following replace happens as ~ is the latex symbol
        # for unbreakable space
        return text.replace("~", " ")

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
        #rendering labels
        self.render_blocks(block.labels)
        return '<math display="block">' + s + '</math>'

    def r_inline_math(self, block):
        s = block.attributes['content']
        #rendering labels
        self.render_blocks(block.labels)
        return '<math>' + s + '</math>'

    def r_align(self, block):
        s = block.attributes['content']
        #rendering labels
        self.render_blocks(block.labels)
        return '<math display="block">\\begin{align}' +\
                    s + '\end{align}</math>'

    def r_gather(self, block):
        s = block.attributes['content']
        output = []
        for eq in s.split("\\\\"):
            eq = eq.replace("\n","").strip()
            output.append('<math display="block">' +\
                        eq + '</math>')
        #rendering labels
        self.render_blocks(block.labels)
        return '\n'.join(output)


    #########################################
    #LABELS and refs

    def r_label(self, block):
        label = block.attributes['label']
        self.tree.addLabel(label)
        return ''

    def r_ref(self, block):
        ref = block.attributes['ref']
        #saving ref in Babel of PageTree
        self.tree.addReference(ref)
        return "{{ref@"+ ref+ "}}"

    #########################################
    #FIGURE

    def r_figure(self, block):
        captions = block.get_children("caption")
        includegraphics = block.get_children("includegraphics")
        s = "[[File:"
        if len(includegraphics):
            inc = includegraphics[0]
            s += inc.attributes["img_name"]
        else:
            return ""
        if len(block.get_children("centering")):
                s += "|" + self.configs["keywords"]["center"]

        if len(captions):
            cap = captions[0]
            s += "|" + cap.attributes["caption"]
        s += "]]"
        return s;



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
            s.append(self.render_children_blocks(item).strip())
            s.append("\n")
        self.list_level = self.list_level[:-1]
        return ''.join(s)

    def r_enumerate(self, block):
        self.list_level += '#'
        s = ['\n']
        for item in block.ch_blocks:
            s.append(self.list_level)
            s.append(self.render_children_blocks(item).strip())
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
        if block.attributes['title'] != None:
            th_title +=" "+ block.attributes['title']
        s = []
        #adding the theorem to the tree
        self.theorem_number += 1
        self.tree.addTheorem(str(self.theorem_number), th_definition)
        #checking if the Environment template is used
        environ = False
        if self.configs['lang'] =='it':
            if th_definition.lower() == 'teorema':
            #adding content to page through a template
                s.append("\n{{InizioTeorema|titolo=" + \
                        th_title+"|number={{thnum@"+ str(self.theorem_number)+"}}"+\
                            "|anchor={{thanchor@"+ str(self.theorem_number) +"}}}}")
                s.append(self.render_children_blocks(block))
                s.append("{{FineTeorema}}\n")
            elif th_definition.lower() == 'definizione':
                s.append("\n{{InizioDefinizione|titolo=" + \
                        th_title+"|number={{thnum@"+ str(self.theorem_number)+"}}"+\
                            "|anchor={{thanchor@"+ str(self.theorem_number) +"}}}}")
                s.append(self.render_children_blocks(block))
                s.append("{{FineDefinizione}}\n")
            elif th_definition.lower() == 'proposizione':
                s.append("\n{{InizioProposizione|titolo=" + \
                        th_title+"|number={{thnum@"+ str(self.theorem_number)+"}}"+\
                            "|anchor={{thanchor@"+ str(self.theorem_number) +"}}}}")
                s.append(self.render_children_blocks(block))
                s.append("{{FineProposizione}}\n")
            elif th_definition.lower() == 'lemma':
                s.append("\n{{InizioLemma|title=" + \
                        th_title+"|number={{thnum@"+ str(self.theorem_number)+"}}"+\
                            "|anchor={{thanchor@"+ str(self.theorem_number) +"}}}}")
                s.append(self.render_children_blocks(block))
                s.append("{{FineLemma}}\n")
            elif th_definition.lower() == 'corollario':
                s.append("\n{{InizioCorollario|titolo=" + \
                        th_title+"|number={{thnum@"+ str(self.theorem_number)+"}}"+\
                            "|anchor={{thanchor@"+ str(self.theorem_number) +"}}}}")
                s.append(self.render_children_blocks(block))
                s.append("{{FineCorollario}}\n")
            elif th_definition.lower()[:-2] == 'eserciz':
                s.append("\n{{InizioEsercizio|titolo=" + \
                        th_title+"|number={{thnum@"+ str(self.theorem_number)+"}}"+\
                            "|anchor={{thanchor@"+ str(self.theorem_number) +"}}}}")
                s.append(self.render_children_blocks(block))
                s.append("{{FineEsercizio}}\n")
            elif th_definition.lower()[:-1] == 'osservazion':
                s.append("\n{{InizioOsservazione|titolo=" + \
                        th_title+"|number={{thnum@"+ str(self.theorem_number)+"}}"+\
                            "|anchor={{thanchor@"+ str(self.theorem_number) +"}}}}")
                s.append(self.render_children_blocks(block))
                s.append("{{FineOsservazione}}\n")
            elif th_definition.lower()[:-2] == 'esemp':
                s.append("\n{{InizioEsempio|titolo=" + \
                        th_title+"|number={{thnum@"+ str(self.theorem_number)+"}}"+\
                            "|anchor={{thanchor@"+ str(self.theorem_number) +"}}}}")
                s.append(self.render_children_blocks(block))
                s.append("{{FineEsempio}}\n")
            elif th_definition.lower() == 'dimostrazione':
                s.append("\n{{InizioDimostrazione|titolo=" + \
                        th_title+"|number={{thnum@"+ str(self.theorem_number)+"}}"+\
                            "|anchor={{thanchor@"+ str(self.theorem_number) +"}}}}")
                s.append(self.render_children_blocks(block))
                s.append("{{FineDimostrazione}}\n")
            else:
                s.append("\n{{Environment|name="+ th_definition + \
                        "|title=" + th_title +\
                        "|content=")
                s.append(self.render_children_blocks(block))
                s.append("}}\n")
        elif self.configs['lang'] =='en':
            if th_definition.lower() == 'theorem':
            #adding content to page through a template
                s.append("\n{{BeginTheorem|title=" + \
                        th_title+"|number={{thnum@"+ str(self.theorem_number)+"}}"+\
                            "|anchor={{thanchor@"+ str(self.theorem_number) +"}}}}")
                s.append(self.render_children_blocks(block))
                s.append("{{EndTheorem}}\n")
            elif th_definition.lower() == 'definition':
                s.append("\n{{BeginDefinition|title=" + \
                        th_title+"|number={{thnum@"+ str(self.theorem_number)+"}}"+\
                            "|anchor={{thanchor@"+ str(self.theorem_number) +"}}}}")
                s.append(self.render_children_blocks(block))
                s.append("{{EndDefinition}}\n")
            elif th_definition.lower() == 'proposition':
                s.append("\n{{BeginProposition|title=" + \
                        th_title+"|number={{thnum@"+ str(self.theorem_number)+"}}"+\
                            "|anchor={{thanchor@"+ str(self.theorem_number) +"}}}}")
                s.append(self.render_children_blocks(block))
                s.append("{{EndProposition}}\n")
            elif th_definition.lower() == 'lemma':
                s.append("\n{{BeginLemma|title=" + \
                        th_title+"|number={{thnum@"+ str(self.theorem_number)+"}}"+\
                            "|anchor={{thanchor@"+ str(self.theorem_number) +"}}}}")
                s.append(self.render_children_blocks(block))
                s.append("{{EndLemma}}\n")
            elif th_definition.lower() == 'corollary':
                s.append("\n{{BeginCorollary|title=" + \
                        th_title+"|number={{thnum@"+ str(self.theorem_number)+"}}"+\
                            "|anchor={{thanchor@"+ str(self.theorem_number) +"}}}}")
                s.append(self.render_children_blocks(block))
                s.append("{{EndCorollary}}\n")
            elif th_definition.lower() == 'exercise':
                s.append("\n{{BeginExercise|title=" + \
                        th_title+"|number={{thnum@"+ str(self.theorem_number)+"}}"+\
                            "|anchor={{thanchor@"+ str(self.theorem_number) +"}}}}")
                s.append(self.render_children_blocks(block))
                s.append("{{EndExercise}}\n")
            elif th_definition.lower() == 'observation':
                s.append("\n{{BeginObservation|title=" + \
                        th_title+"|number={{thnum@"+ str(self.theorem_number)+"}}"+\
                            "|anchor={{thanchor@"+ str(self.theorem_number) +"}}}}")
                s.append(self.render_children_blocks(block))
                s.append("{{EndObservation}}\n")
            elif th_definition.lower() == 'remark':
                s.append("\n{{BeginRemark|title=" + \
                        th_title+"|number={{thnum@"+ str(self.theorem_number)+"}}"+\
                            "|anchor={{thanchor@"+ str(self.theorem_number) +"}}}}")
                s.append(self.render_children_blocks(block))
                s.append("{{EndRemark}}\n")
            elif th_definition.lower() == 'example':
                s.append("\n{{BeginExample|title=" + \
                        th_title+"|number={{thnum@"+ str(self.theorem_number)+"}}"+\
                            "|anchor={{thanchor@"+ str(self.theorem_number) +"}}}}")
                s.append(self.render_children_blocks(block))
                s.append("{{EndExample}}\n")
            elif th_definition.lower() == 'demonstration':
                s.append("\n{{BeginDemonstration|title=" + \
                        th_title+"|number={{thnum@"+ str(self.theorem_number)+"}}"+\
                            "|anchor={{thanchor@"+ str(self.theorem_number) +"}}}}")
                s.append(self.render_children_blocks(block))
                s.append("{{EndDemonstration}}\n")
            else:
                s.append("\n{{Environment|name="+ th_definition + \
                        "|title=" + th_title +\
                        "|content=")
                s.append(self.render_children_blocks(block))
                s.append("}}\n")
        #exit from theorem ambient
        self.tree.exitTheorem()
        return '\n'.join(s)

    def r_proof(self, block):
        s=[]
        if self.configs['lang'] == 'it':
            if block.title !=None:
                s.append('\n{{InizioDimostrazione|titolo='+\
                        block.attributes['title']+ "}}")

                s.append(self.render_children_blocks(block))
                s.append("{{FineDimostrazione}}\n")
            else:
                s.append('\n{{InizioDimostrazione}}')
                s.append(self.render_children_blocks(block))
                s.append("{{FineDimostrazione}}\n")
        elif self.configs['lang'] == 'en':
            if block.title !=None:
                s.append('\n{{BeginProof|title='+\
                        block.attributes['title']+"}}")
                s.append(self.render_children_blocks(block))
                s.append("{{EndProof}}\n")
            else:
                s.append('\n{{BeginProof}}')
                s.append(self.render_children_blocks(block))
                s.append("{{EndProof}}\n")
        return '\n'.join(s)

    #########################################
    #ACCENTED letters
    def r_accented_letter(self, block):
        if block.attributes["accent_type"] == '"' \
                and block.attributes["letter"] == "a":
            return "ä"
        if block.attributes["accent_type"] in ["'","`"]:
            return block.attributes["letter"]+\
                    block.attributes["accent_type"]
        else:
            return block.attributes["letter"]
