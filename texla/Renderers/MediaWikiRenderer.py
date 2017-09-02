import logging
from .Renderer import Renderer
from .Renderer import render_hook
from ..PageTree.PageTree import *

class MediaWikiRenderer(Renderer):

    def __init__(self, configs, reporter):
        super().__init__(configs, reporter)
        self.doc_title = configs['doc_title']
                #PageTree object
        self.tree = PageTree(configs, reporter)
        #parameter for list formatting
        self.list_level = ''
        #parameters for theorem handling
        self.in_theorem = False
        self.theorem_number = 0
        self.th_numbering = {}

    ########################################
    #STARTING POINT

    def start_rendering(self, parser_tree_explorer):
        """
        Entrypoint for rendering. It requires the
        tree of parsed blocks as parameter
        """
        #start rendering of Rendering base class to activate plugins...
        super(MediaWikiRenderer, self).start_rendering(parser_tree_explorer)
        root_block =  self.parser_tree_explorer.root_block
        #start the rendering from root_block
        self.render_block(root_block)
        #after rendering for PageTree structure
        self.tree.after_render()
        #end rendering of base class to stop plugins
        super(MediaWikiRenderer, self).end_rendering()
        #return the PageTree as a result
        return self.tree

    ####### ROOT BLOCK
    @render_hook("root-block")
    def r_document(self, block):
        #we trigger the rendering of content
        text = self.render_children_blocks(block)
        #text is the tex outside sections
        self.tree.addText(text)
        #returning the text to respect the interface
        return text

    ########################################
    #DEFAULT

    @render_hook("default")
    def default(self, block):
        #we don't print anything
        return ''

    #########################################
    #TEXT
    @render_hook("text")
    def r_text(self, block):
        text = block.attributes['text']

        # The following replace happens as ~ is the latex symbol
        # for unbreakable space
        return text.replace("~", " ")

    @render_hook("newline")
    def r_newline(self, block):
        return '\n'

    @render_hook("newpage")
    def r_newpage(self, block):
        return '\n\n'

    @render_hook("par")
    def r_par(self, block):
        return '\n\n'

    #########################################
    #SECTIONING

    @render_hook("part", "chapter", "section", "subsection",
                 "subsubsection", "paragraph", "subparagraph")
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

    @render_hook("displaymath", "equation")
    def r_display_math(self, block):
        s = block.attributes['content']
        #rendering labels
        self.render_blocks(block.labels)
        return '<math display="block">' + s + '</math>'

    @render_hook("inlinemath", "ensuremath")
    def r_inline_math(self, block):
        s = block.attributes['content']
        #rendering labels
        self.render_blocks(block.labels)
        return '<math>' + s + '</math>'

    @render_hook("align", "eqnarray", "multline", "alignat")
    def r_align(self, block):
        s = block.attributes['content']
        #rendering labels
        self.render_blocks(block.labels)
        return '<math display="block">\\begin{align}' +\
                    s + '\end{align}</math>'

    @render_hook("gather")
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

    @render_hook("label")
    def r_label(self, block):
        label = block.attributes['label']
        self.tree.addLabel(label)
        return ''

    @render_hook("ref", "vref", "pageref", "eqref")
    def r_ref(self, block):
        ref = block.attributes['ref']
        #saving ref in Babel of PageTree
        self.tree.addReference(ref)
        return "{{ref@"+ ref+ "}}"

    #########################################
    #FIGURE

    @render_hook("figure")
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
        return s



    #########################################
    #FORMATTING

    @render_hook("%", "&", "$", "{", "}", "#", "_")
    def r_special_character(self, block):
        return block.attributes['character']

    @render_hook("dots", "ldots")
    def r_dots(self, block):
        return '...'

    @render_hook("textbf")
    def r_textbf(self, block):
        s = []
        s.append("\'\'\'")
        s.append(self.render_children_blocks(block))
        s.append("\'\'\'")
        return ''.join(s)

    @render_hook("textit", "emph")
    def r_textit(self, block):
        s = []
        s.append("\'\'")
        s.append(self.render_children_blocks(block))
        s.append("\'\'")
        return ''.join(s)

    @render_hook("textsc")
    def r_textsc(self, block):
        return self.render_children_blocks(block).upper()

    @render_hook("textsuperscript")
    def r_superscript(self, block):
        s = []
        s.append('<sup>')
        s.append(self.render_children_blocks(block))
        s.append('</sup>')
        return ''.join(s)

    @render_hook("textsubscript")
    def r_subscript(self, block):
        s = []
        s.append('<sub>')
        s.append(self.render_children_blocks(block))
        s.append('</sub>')
        return ''.join(s)

    @render_hook("underline", "uline")
    def r_underline(self, block):
        s = []
        s.append('{{Sottolineato|')
        s.append(self.render_children_blocks(block))
        s.append('}}')
        return ''.join(s)

    @render_hook("abstract")
    def r_abstract(self, block):
        s = []
        s.append('{{Abstract|')
        s.append(self.render_children_blocks(block))
        s.append('}}')
        return ''.join(s)

    @render_hook("linebreak", "pagebreak", "nolinebreak", "nopagebreak")
    def r_break(self, block):
        return ''

    @render_hook("vspace")
    def r_vspace(self,block):
        return '\n\n'

    @render_hook("mandatory_space")
    def r_mandatory_space(self,block):
        return ' '

    @render_hook("verbatim")
    def r_verbatim(self, block):
        return '<pre>' + block.attributes['content'] +'</pre>'

    @render_hook("verb")
    def r_verb(self, block):
        return '<tt>' + block.attributes['content'] +'</tt>'

    #########################################
    #ALIGNMENT

    @render_hook("center", "centerline")
    def r_center(self, block):
        s = []
        s.append('{{Center|')
        s.append(self.render_children_blocks(block))
        s.append('}}')
        return ''.join(s)

    @render_hook("flushleft")
    def r_flushleft(self, block):
        s = []
        s.append('{{Flushleft|')
        s.append(self.render_children_blocks(block))
        s.append('}}')
        return ''.join(s)

    @render_hook("flushright")
    def r_flushright(self, block):
        s = []
        s.append('{{Flushright|')
        s.append(self.render_children_blocks(block))
        s.append('}}')
        return ''.join(s)

    #########################################
    #LISTS

    @render_hook("itemize")
    def r_itemize(self, block):
        self.list_level += '*'
        s = ['\n']
        for item in block.ch_blocks:
            s.append(self.list_level)
            s.append(self.render_children_blocks(item).strip())
            s.append("\n")
        self.list_level = self.list_level[:-1]
        return ''.join(s)

    @render_hook("enumerate")
    def r_enumerate(self, block):
        self.list_level += '#'
        s = ['\n']
        for item in block.ch_blocks:
            s.append(self.list_level)
            s.append(self.render_children_blocks(item).replace('\n', ''))
            s.append("\n")
        self.list_level = self.list_level[:-1]
        return ''.join(s)

    @render_hook("description")
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

    @render_hook("quotation", "quote")
    def r_quotes(self, block):
        s = []
        s.append('<blockquote>')
        s.append(self.render_children_blocks(block))
        s.append('</blockquote>')
        return ''.join(s)

    @render_hook("verse")
    def r_verse(self, block):
        s = []
        s.append('<blockquote>')
        s.append('\n'.join(self.render_children_blocks(block).split('//')))
        s.append('</blockquote>')
        return ''.join(s)

    @render_hook("footnote")
    def r_footnote(self, block):
        s = []
        s.append("<ref>")
        s.append(self.render_children_blocks(block))
        s.append("</ref>")
        return ''.join(s)

    ########################################
    #Code

    @render_hook("lstlisting")
    def r_lstlisting(self, block):
        s = []
        if "language" in block.options:
            s.append('<source lang="{}" line>'.format(block.options["language"]))
        else:
            #check if there are any lstset block
            query = self.parser_tree_explorer.query_block_by_name("lstset")
            if len(query) == 0:
                s.append('<source line>')
            else:
                s.append('<source lang="{}" line>'.format(query[0].options["language"]))
        s.append(block.content)
        s.append('</source>')
        return '\n'.join(s)

    @render_hook("texttt")
    def r_quotes(self, block):
        s = []
        s.append('<code>')
        s.append(self.render_children_blocks(block))
        s.append('</code>')
        return ''.join(s)

    #########################################
    #Theorems

    @render_hook("theorem")
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

    @render_hook("proof")
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

    @render_hook("accented_letter")
    def r_accented_letter(self, block):
        if block.attributes["accent_type"] == '"' \
                and block.attributes["letter"] == "a":
            return "ä"
        if block.attributes["accent_type"] in ["'","`"]:
            return block.attributes["letter"]+\
                    block.attributes["accent_type"]
        else:
            return block.attributes["letter"]
