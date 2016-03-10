# -*- coding: utf-8 -*-
import string,re
import subprocess
import tikz2svg
from plasTeX.Renderers import Renderer
from plasTeX import Command, Environment
from PageTree import *
from utility import *
from MathParser import *

class MediaWikiRenderer (Renderer):

    outputType = unicode
    fileExtension = '.mw'

    aliases = {
        'superscript': 'active::^',
        'subscript': 'active::_',
        'dollar': '$',
        'percent': '%',
        'opencurly': '{',
        'closecurly': '}',
        'underscore': '_',
        'ampersand': '&',
        'hashmark': '#',
        'space': ' ',
        'tilde': 'active::~',
        'at': '@',
        'backslash': '\\',
        #math starred commmands
        'equation_star':'equation*',
        'eqnarray_star':'eqnarray*',
        'align_star':'align*',
        'alignat_star':'alignat*',
        'multline_star':'multline*',
        'gather_star':'gather*',
        'paragraph_star':'paragraph*'
    }

    '''List of nodes not to explore'''
    no_enter = ['titlepage','tableofcontents','pagestyle','maketitle',
            'numberwithin','geometry',"index","pspicture"]

    ##############################################################
    #initialization
    def __init__(self, configs,*args, **kwargs):
        Renderer.__init__(self, *args, **kwargs)
        #document title
        self.configs = configs
        self.doc_title = configs['title']
        self.image_extension = configs['images_ext']
        # Load dictionary with methods
        for key in dir(self):
            if key.startswith('do__'):
                self[self.aliases[key[4:]]] = getattr(self, key)
            elif key.startswith('do_'):
                self[key[3:]] = getattr(self, key)

        self['default-layout'] = self['document-layout'] = self.default
        #tree object
        self.tree = PageTree(self.doc_title,
                configs['output_path'],configs)
        #parameter for list formatting
        self.list_level=u''
        #parameter for theorem handling
        self.in_theorem=False

        ####### TAGS ANALYSY
        #dictionary for tag usage
        self.used_tags = {}

    '''function that register user defined theorem
    to the theorem function. Moreover it register a dictionary
    for theorem numbering'''
    def init_theorems(self, th_dict):
        self.th_dict= th_dict
        self.th_numb={}
        for key in th_dict:
            #adding key in theorem numbering dict
            self.th_numb[key]=0

    '''Function that save a tikz sources dictionary {tikz1:'source',...}
    for rendering in do_tikzpicture and do_tikz'''
    def init_tikz_images(self,tikz_dict,tikzcom_dict):
        self.tikz_images = tikz_dict
        self.tikzcom_images = tikzcom_dict

    #####################################
    #Utils for debug
    def used_tag(self,tag):
        if tag in self.used_tags:
            self.used_tags[tag]+=1
        else:
            self.used_tags[tag]=1

    ###################################
    #defaul tags
    def default(self, node):
        if node.nodeName in self.no_enter:
            self.used_tag('NO-ENTER@'+ node.nodeName)
            return u''
        self.used_tag('DEFAULT@'+ node.nodeName)
        #return content
        return unicode(node).lstrip()

    def do_textDefault(self, node):
        self.used_tag('TEXT-DEFAULT')
        text = unicode(node).lstrip()
        return text

    ###############################
    #sectioning
    def sectioning(self, node,page_type):
        title = unicode(node.attributes['title'])
        #remove the \n insiede title
        title = re.sub('\\n*','',title)
        #fixing wrong symbolds
        title = title.replace(u'’',u"'")
        title = title.replace(u'`',u"'")
        #adding index to parent
        self.tree.addToSubpageIndex(title)
        #creation of the new page
        self.tree.createPage(title,page_type)
        #content processing
        text = unicode(node).lstrip()
        #adding text to current page
        self.tree.addText(text)
        #exiting the section
        self.tree.exitPage()

    def do_part (self,node):
        self.used_tag('PART')
        self.sectioning(node,'part')
        return u''

    def do_chapter (self,node):
        self.used_tag('CHAPTER')
        self.sectioning(node,'chapter')
        return u''

    def do_section(self,node):
        self.used_tag('SECTION')
        self.sectioning(node,'section')
        return u''

    def do_subsection(self,node):
        self.used_tag('SUBSECTION')
        self.sectioning(node,'subsection')
        return u''

    def do_subsubsection(self,node):
        self.used_tag('SUBSUBSECTION')
        self.sectioning(node,'subsubsection')
        return u''

    def do_paragraph(self,node):
        self.used_tag('PARAGRAPH')
        self.sectioning(node,'paragraph')
        return u''

    do__paragraph_star = do_paragraph
    #################################################

    #subparagraph are not node of the section tree
    def do_subparagraph(self,node):
        self.used_tag('SUBPARAGRAPH')
        s =[]
        s.append('\n\'\'\'')
        s.append(unicode(node.attributes['title']))
        s.append('\'\'\'\'')
        s.append(unicode(node).lstrip())
        return u''.join(s)

    '''Enter point for parsing. Root page is already created'''
    def do_document(self,node):
        self.used_tag('DOCUMENT')
        content = unicode(node).lstrip()
        self.tree.addText(content)
        return u'%s' % content


    ###############################################
    #references
    ''' Method that insert label into PageTree'''
    def label(self,label):
        self.used_tag('LABEL')
        #the reference to the current page is saved
        if self.in_theorem:
            self.tree.addLabel_insideTheorem(label)
        else:
            self.tree.addLabel(label)

    def labels(self,lbls):
        for l in lbls:
            self.label(l)

    ''' Labels are managed bey PageTree'''
    def do_label(self,node):
        #retriving label id
        l = node.attributes['label']
        #saving label
        self.label(l)
        return u''

    '''All ref tag are substituted by normal ref tag.
    It'll be reparsed after text collapsing'''
    def do_ref(self,node):
        self.used_tag('REF')
        r = node.attributes['label']
        return unicode('\\ref{'+r+'} ')

    do_pageref = do_ref
    do_vref = do_ref
    do_eqref = do_ref

    ################################################
    #Formatting
    '''Paragraph'''
    def do_par(self, node):
        self.used_tag('PAR')
        s = []
        s.append(u'\n\n')
        s.append(unicode(node).lstrip())
        return u''.join(s)

    '''Breaks line inside a paragraph'''
    def do_newline(self,node):
        self.used_tag('NEWLINE')
        return u'\n'

    do__backslash = do_newline
    do_linebreak = do_newline

    def do_newpage(self,node):
        self.used_tag('NEWPAGE')
        s = []
        s.append(u'')
        s.append(unicode(node).lstrip())
        return u''.join(s)

    def do_textbf(self,node):
        self.used_tag('TEXTBF')
        s=[]
        s.append(u"\'\'\'")
        s.append(unicode(node).lstrip())
        s.append(u"\'\'\'")
        return u''.join(s)

    def do_textit(self,node):
        self.used_tag('TEXTIT')
        s=[]
        s.append(u"\'\'")
        s.append(unicode(node).lstrip())
        s.append(u"\'\'")
        return u''.join(s)

    def do_textsc(self,node):
        self.used_tag('TEXTSC')
        return unicode(node).lstrip().upper()

    do_emph = do_textit
    do_itshape = do_textit
    do_textsl = do_textit
    do_slshape = do_textit

    def do_itemize(self,node):
        self.used_tag('ITEMIZE')
        s = []
        self.list_level+=u'*'
        for item in node.childNodes:
            t=unicode(item).lstrip()
            s.append(self.list_level+t)
        self.list_level = self.list_level[:-1]
        return u'\n'.join(s)

    def do_enumerate(self,node):
        self.used_tag('ENUMERATE')
        s = []
        self.list_level+=u'#'
        for item in node.childNodes:
            t=unicode(item).lstrip()
            s.append(self.list_level+t)
        self.list_level = self.list_level[:-1]
        return u'\n'.join(s)

    def do_description(self,node):
        self.used_tag('DESCRIPTION')
        s = []
        for item in node.childNodes:
            t=unicode(item).lstrip()
            s.append(u';'+ str(item.attributes['term'])+":" +t)
        return u'\n'.join(s)

    def do__tilde(self,node):
        return unicode(node)

    def do__dollar(self,node):
        return u'$'

    def do__percent(self,node):
        return u'%'

    def do__opencurly(self,node):
        return u'{'

    def do__closecurly(self,node):
        return u'}'

    def do__hashmark(self,node):
        return u'#'

    def do__underscore(self,node):
        return u'_'

    def do__ampersand(self,node):
        return u'&'

    def do_quotation(self, node):
        self.used_tag('QUOTATION')
        s = []
        s.append(u'<blockquote>')
        s.append(unicode(node).lstrip())
        s.append(u'</blockquote>')
        return u''.join(s)

    do_quote=do_quotation
    do_verse=do_quotation

    def do_href(self,node):
        return unicode(node.attributes['url'])

    def do_centering(self, node):
        self.used_tag('CENTERING')
        s = []
        s.append(u'<div style="text-align:center;">')
        s.append(unicode(node).lstrip())
        s.append(u'</div>')
        return u''.join(s)

    do_center = do_centering

    def do_flushright(self, node):
        self.used_tag('FLUSHRIGHT')
        s = []
        s.append(u'<div style="text-align:right;">')
        s.append(unicode(node).lstrip())
        s.append(u'</div>')
        return u''.join(s)

    def do_flushleft(self, node):
        self.used_tag('FLUSHLEFT')
        return unicode(node).lstrip()

    def do_footnote(self,node):
        self.used_tag('FOOTNOTE')
        s=[]
        s.append(u"<ref>")
        s.append(unicode(node).lstrip())
        s.append(u"</ref>")
        return u''.join(s)

    def do_hrulefill(self,node):
        self.used_tag('HRULEFILL')
        return u'----'

    do_rule=do_hrulefill

    def do_vspace(self,node):
        return u''

    def do_textrm(self, node):
        self.used_tag('TEXTRM')
        return unicode(node)

    def do_small(self, node):
        self.used_tag('SMALL')
        s = []
        s.append(u'<small>')
        s.append(unicode(node).lstrip())
        s.append(u'</small>')
        return u''.join(s)

    do_tiny=do_small
    do_scriptsize=do_small

    def do_underline(self, node):
        self.used_tag('UNDERLINE')
        s = []
        s.append(u'<u>')
        s.append(unicode(node).lstrip())
        s.append(u'</u>')
        return u''.join(s)

    do_underbar=do_underline
    do_uline = do_underline

    def do_texttt(self,node):
        self.used_tag('TEXTTT')
        s=[]
        s.append(u"<code>")
        s.append(unicode(node).lstrip())
        s.append(u"</code>")
        return u''.join(s)

    def do_verbatim(self,node):
        self.used_tag('VERBATIM')
        s=[]
        s.append(u' <nowiki>')
        source = node.source
        source = source.replace("\\begin{verbatim}", "")
        source = source.replace("\\end{verbatim}", "")
        for line in source.split('\n'):
            s.append(" %s" % line)
        s.append(u' </nowiki>\n')
        return u'\n'.join(s)

    ##########################################
    #Figures and Tikz

    '''The figure environment is handled with regexs. '''
    def do_figure(self,node):
        self.used_tag('FIGURE')
        file_path=''
        caption = ''
        label=''
        #searchin includegraphics
        graphics_search = re.search(ur'\\includegraphics\s*(\[.*?\])*\s*{(.*?)}',
                                    node.source)
        if graphics_search:
            file_path = graphics_search.group(2).split('/').pop()
            #file_path+='.'+ self.configs['image_extension']
        #searching label
        label_search = re.search(ur'\\label{(.*?)}',node.source)
        if label_search:
            label = label_search.group(1)
        #searching caption
        caption = get_content_greedy(node.source, '\\caption')
        #creating figure
        f = Figure(label,caption,file_path)
        #adding figure to tree
        self.tree.addFigure(f)
        #adding label
        if label:
            self.label(label)
        #return warning text for figure
        if caption != '':
            return unicode('[[File:'+file_path+']]\n')
        else:
            return unicode('[[File:'+file_path+']]\n')

    do_wrapfigure = do_figure

    def do_tikz(self,node):
        if not hasattr(self,'picture_nrcom'):
            self.picture_nrcom = 1
        else:
            self.picture_nrcom += 1
        file_out = open('./tikzcom'+ str(self.picture_nrcom) + '.svg','w+')
        file_out.write(tikz2svg.tikz2svg(self.tikzcom_images['tikz'+ str(self.picture_nrcom)]))
        file_out.close()
        return u'[[File:tikzcom' + unicode(self.picture_nrcom) + u'.svg]]'

    def do_tikzpicture(self,node, label=''):
        if not hasattr(self,'picture_nr'):
            self.picture_nr = 1
        else:
            self.picture_nr += 1
        if label=='':
            label = 'tikz '+ str(self.picture_nr) + '.svg'
        file_out = open(label + '.svg','w+')
        file_out.write(tikz2svg.tikz2svg(self.tikz_images['tikz'+ str(self.picture_nr)]))
        file_out.close()
        return u'[[File:'+ label +']]'

    ##########################################################à
    #Tables

    '''The Table environment is handled with regex'''
    def do_table(self,node):
        self.used_tag('TABLE')
        caption = ''
        label = ''
        #searching label
        label_search = re.search(ur'\\label{(.*?)}',node.source)
        if label_search:
            label = label_search.group(1)
        #searching caption
        caption = get_content_greedy(node.source, '\\caption')
        #creating table
        t = Table(label,caption)
        #adding table to the tree
        self.tree.addTable(t)
        #adding label
        if label:
            self.label(label)
        #elaborating child nodes (tabular)
        return unicode(node)

    '''Counter for orphan (outside table) tabular'''
    tabular_counter = 0

    '''Tabular environment should be inside a table environment.
    If not, the table is marks'''
    def do_tabular(self,node):
        self.tabular_counter+=1
        self.used_tag('TABULAR')
        label = 'table'+str(self.tabular_counter)
        #creating table
        t = Table(label,label)
        #adding table to the tree
        self.tree.addTable(t)
        tablestring = ''
        # Iterate through all rows in the table
        for rownum, row in enumerate(node):
            if rownum != 0:
                    tablestring += '|-\n'
            # Iterate through all cells in the row
            for cellnum, cell in enumerate(row):
                colspan = cell.attributes.get('colspan', 1)
                # Print the text and align
                align = cell.style['text-align']
                if align != "left":
                    tablestring += '|align\"' + cell.style['text-align'] + \
                            '\" | ' + cell.textContent.strip() + '\n'
                else:
                    tablestring += '|' + cell.textContent.strip() + '\n'
        return unicode('{|class=\"table-bordered wikitable\"\n'+tablestring+'|}')


    ###################################################
    #Math tags

    '''Handles math inside a displaymath mode:
    -it removes $$ and \[ \].
    -it remove \begin and \end so it has to be used
    only for \begin{equation} and \begin{displaymath}.
    Other \begin{math_environment} that are not inside a displaymath
    have to be handled by specific methods'''
    def handleDisplayMath(self, node, env='equation'):
        self.used_tag('DISPLAY_MATH@'+env )
        s = node.source
        #get content of environment or display math tags
        content = get_environment_content(s,env)[0]
        if content:
            s = content
        else:
            '''if there is no environment we have
            remove the $$..$$ or \[..\]'''
            content2 = get_content_display_math(s)
            if content2:
                s = content2
        #check math content
        s = math_check(s, env)
        #search label
        labels, s = get_labels(s)
        if labels:
            #adding label to tree
            self.labels(labels)
        return '<dmath>' + s + '</dmath>'

    #displaymath is converted to \[..\]
    do_displaymath = handleDisplayMath
    do_equation = handleDisplayMath

    def do_subequations(self,node):
        return self.handleDisplayMath(node,'subequations')

    def do__equation_star(self,node):
        return self.handleDisplayMath(node,'equation\\*')

    '''Handles inline math ( $..$ \( \) ) '''
    def do_math(self, node):
        self.used_tag('MATH')
        s = node.source
        #get content
        content = get_content_inline_math(s)
        if content:
            s = content
        #check math content
        s = math_check(s)
        #search label
        labels, s = get_labels(s)
        if labels:
            #adding label to tree
            self.labels(labels)
        return '<math>'+s+'</math>'

    '''Check math inside macros'''
    def do_ensuremath(self,node):
        self.used_tag('ENSURE_MATH')
        s = node.source
        print s
        #removing \ensuremath{}
        s = remove_command_greedy(s,'\\ensuremath',False)
        print s
        #check math content
        s = math_check(s)
        return '<math>'+ s +'</math>'

    '''Support for align type tags.
    They are outside math modes an supported directly'''
    def do_align(self, node):
        self.used_tag('MATH_ALIGN')
        s = node.source
        #replace eqnarray,multline,alignat with align
        s = s.replace('alignat',u'align')
        s = s.replace('eqnarray',u'align')
        s = s.replace('multline',u'align')
        s = s.replace('align*',u'align')
        s = s.replace('alignat*',u'align')
        s = s.replace('eqnarray*',u'align')
        s = s.replace('multline*',u'align')
        #get content of environment
        content = get_environment_content(s,'align')[0]
        if content:
            s = content
        #check math content
        s = math_check(s)
        #search label
        labels,s = get_labels(s)
        s_tag='<dmath type="align">'
        if labels:
            #adding label to tree
            self.labels(labels)
            s_tag = '<dmath type="align">'
        return s_tag + s + '</dmath>'

    do_eqnarray = do_align
    do_multline = do_align
    do_alignat =  do_align
    #using aliases
    do__align_star = do_align
    do__alignat_star = do_align
    do__eqnarray_star = do_align
    do__multline_star = do_align

    ''' Support for gather alignment style '''
    def do_gather(self, node, env='gather'):
        self.used_tag("MATH_GATHER")
        s = node.source
        #get content
        content = get_environment_content(s,env)[0]
        if content:
            s = content
        result = []
        #splitting every new line in gather
        #creating separated dmath tag
        eqs = s.split('\\\\')
        for eq in eqs:
            #check math
            eq = math_check(eq)
            #getting label
            labels,s = get_labels(eq)
            if labels:
                self.labels(labels)
            result.append('<dmath>'+ eq+'</dmath>')
        return u'\n'.join(result)

    def do__gather_star(self,node):
        return self.do_gather(node, env='gather\*')


    ###############################################
    #Theorems handling
    '''Methods that handles theorems defined in the .thms config file.
    It extracts name and create a indexable title (====)'''
    def do_theorem(self,node):
        self.used_tag("THEOREM")
        self.in_theorem= True
        #reading id
        th_id = node.attributes['th_id']
        #reading title
        th_title = ''
        if node.attributes['th_title']!=None:
            th_title = node.attributes['th_title'].strip()
        #reading name form thms dict
        th_name = self.th_dict[th_id]
        #update theorem numbering
        if not th_id.endswith('*'):
            num = self.th_numb[th_id]+1
            self.th_numb[th_id] = num
            #adding numb to name
            th_name += " "+str(num)
        #add theorem to PageTree
        self.tree.addTheorem(th_name +" " + th_title)
        #adding content to page through a template
        s =[]
        s.append("{{Environment|name="+th_name+'|title=' + \
            th_title+"|content=")
        #elaborating childnodes
        s.append(unicode(node).lstrip()+'\n')
        #closing template
        s.append("}}")
        #exiting theorem env
        self.in_theorem=False
        return u'\n'.join(s)

    def do_proof(self,node):
        self.used_tag('PROOF')
        proof_name = ''
        if node.attributes['proof_name']!=None:
            proof_name = node.attributes['proof_name']
        s=[]
        s.append("{{Environment|name="+self.configs['keywords']['proof'])
        if proof_name!="":
            s.append(" ("+proof_name+")")
        s.append("|content=")
        s.append(unicode(node).lstrip())
        s.append('}}\n')
        return u''.join(s)


    ####################################################
    #Code Environments

    def do_lstdefinestyle(self,node):
        if not hasattr(self, 'style_lang'):
            self.style_lang = dict([])
        name = unicode(node.attributes['name'].source)
        args = unicode(node.attributes['args'].source)
        a = []
        for i in args.split(','):
            a.append(i+'= ')
        argsdict = {arg.split('=')[0].strip(): arg.split('=')[1] for arg in (a)}
        if 'language' in argsdict:
            self.style_lang[name] = argsdict['language']
        else:
            self.style_lang[name] = 'Not specified in style'
        return u''

    def do_lstset(self,node):
        args = unicode(node.attributes['args'])
        a = []
        for i in args.split(','):
            a.append(i+'= ')
        argsdict = {arg.split('=')[0].strip(): arg.split('=')[1] for arg in (a)}
        if 'language' in argsdict:
            self.lst_lang = argsdict['language']
        elif 'style' in argsdict:
            self.lst_lang = self.style_lang[argsdict['style']]
        else:
            self.lst_lang = 'Not specified'
        print self.lst_lang
        return u''

    def do_lstlisting(self,node):
        self.used_tag('LSTLISTING')
        s=[]
        source = node.source
        s.append('<source lang="'+self.lst_lang+'">')
        #ignore formatting from \lstlisting
        if source.find('}')+1==source.find('['):
            ind1 = source.find(']')
        else:
            ind1 = source.find('}')
        ind2 = source.rfind('\\')
        print(source)
        s.append(source[ind1+1:ind2])
        s.append('</source>\n')
        return u'\n'.join(s)

    def do_minted(self,node):
        self.used_tag('MINTED')
        s=[]
        source = node.source
        lang = source[source.find('}'):]
        lang = lang[lang.find('{')+1:]
        #ignore formatting from \minted
        source = lang[lang.find('}')+1:]
        lang = lang[:lang.find('}')]
        self.minted_lang = lang
        s.append('<source lang="'+self.minted_lang+'">')
        ind2 = source.rfind('\\')
        s.append(source[:ind2])
        s.append('</source>\n')
        return u'\n'.join(s)
