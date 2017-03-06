from .Page import Page
from .Babel import Babel
from .TheoremsManager import *
import re, os, json


class PageTree():
    def __init__(self, configs, reporter):
        self.configs = configs
        self.reporter = reporter
        self.doc_title = configs['doc_title']
        self.keywords = configs['keywords']
        self.output_path = configs['output_path']
        #pages Data  {id: page}
        self.pages = {}
        #id : titles
        self.titles = {}
        #label manager
        self.babel = Babel(reporter)
        #theorems manager
        self.theorems_manager = TheoremsManager(self.pages)
        #urls (they are created after collapsing).
        #it's a dictionary id:url
        self.urls = {}
        #ROOT PAGE
        ro = Page(self.doc_title, 'root', -1, self.keywords)
        self.root_id = ro.id
        self.root_page = ro
        self.pages[self.root_id] = ro
        self.titles[self.root_id] = ro.title
        #indexes
        self.pageid_stack = [ro.id]
        self.current_page_id = self.root_id
        #the anchor is the object to be referentiated by labels
        self.current_anchor = ro

    def createPage(self, title, page_type):
        """This method creates a new page and enters
        in his enviroment setting current variables"""
        title = self.get_normalized_title(title)
        #finding level
        level = len(self.pageid_stack) - 1
        #create new page
        p = Page(title, page_type, level, self.keywords)
        #add page to pages index
        self.pages[p.id] = p
        self.titles[p.id] = p.title
        #adding the page as subpage of the current page
        self.pages[self.current_page_id].addSubpage(p)
        #updates current
        self.pageid_stack.append(p.id)
        self.current_page_id = p.id
        self.current_anchor = p

    def exitPage(self):
        """Return to the parent page enviroment"""
        self.current_page_id = self.pageid_stack[-2]
        self.pageid_stack.pop()
        self.current_anchor = self.pages[self.current_page_id]

    def addText(self, text):
        self.pages[self.current_page_id].addText(text)

    def addLabel(self, label):
        """adding label to the babel with the current
        page as the anchor"""
        self.babel.add_label(label, self.current_anchor)

    def addReference(self, label):
        """adding the current_anchor as a reference for the
        requesting label"""
        self.babel.add_reference(label, self.current_anchor)

    def addTheorem(self, id, th_type):
        """Adding a theorem also as anchor"""
        th = Theorem(id,self.current_anchor, th_type)
        self.theorems_manager.addTheorem(th)
        #setting current anchor on the theorem
        self.current_anchor = th

    def exitTheorem(self):
        """Removing the anchor from the theorem and setting it
        to the last used page"""
        self.current_anchor = self.pages[self.current_page_id]

    @staticmethod
    def get_normalized_title(title):
        """Function that removes bad symbols from title"""
        title = title.replace('$', '')
        title = title.replace('{','')
        title = title.replace('}','')
        title = title.replace('\\mathcal','')
        title = title.replace('\\mathbf','')
        title = title.replace('\\mathbb','')
        title = title.replace('\\ensuremath','')
        title = title.replace('&', 'e')
        title = title.replace('\\', '')
        title = title.replace('/', '_')
        title = title.replace('>', 'gt')
        title = title.replace('<', 'lt')
        title = title.replace(':',' ')
        title = title.replace('.',' ')
        title = title.replace(',',' ')
        title = title.replace(';',' ')
        return title

    def get_tree_json(self):
        """This function return the json tree"""
        return self.root_page.get_json_dictionary(self.pages)

    def get_tree_debug(self):
        """This function prints the tree for debug"""
        s = []
        for p in self.root_page.get_subpages():
            s.append(p.get_str())
        return('\n'.join(s))

    def after_render(self):
        """This function does some fixes after rendering"""
        for page in self.pages.values():
            page.after_render()

    def change_title(self, page_id, title):
        self.pages[page_id].title = title


    def remove_page_from_tree(self, page, parent=None):
        """This function remove a page from the tree,
        but doesn't delete it. The page remains in the self.pages
        dictionary but not in the subpages of the pages in the tree.
        If a parent page is passed the research for the removal
        starts from that page with performance improvements"""
        if parent:
            parent.removeSubpage(page)
        else:
            self.root_page.removeSubpage(page)

    def move_page_references(self, oldpage, newpage):
        """This function fixes the reference in TheoremsManager
        and Babel when a page is moved"""
        #we need to fix anchors in Babel
        self.babel.move_anchor(oldpage, newpage)
        #we need also to fix the theorems page
        self.theorems_manager.move_theorems_page(oldpage, newpage)


    def collapse_tree(self, content_level, max_page_level):
        """This function contains all the tree collapsing
        procedures in the order:
        1) Mark the pages for the content collapsing without
           actually move the text
        2) Fix the tree order with collapsing of page level
           (N.B.: it needs the collasped status of pages)
        3) Fix the urls now that the level if fixed.
        4) Create the pagenumber of every page, after the
           movement in the tree.
        5) The theorems are fixed adding the right numbering.
        6) Fix references to labels: the Babel will change pages
           content so this has to be done after the url fixing
           but before the actual text collapsing.
        7) Finally collapse the pages text to the
           right content level"""
        self.collapse_content_level(content_level)
        self.collapse_page_level(max_page_level)
        self.collapse_urls()
        self.create_pagenumbers()
        self.theorems_manager.fix_theorems()
        #ask the babel to fix the refs to labels in all the pages
        self.babel.fix_references()
        #collapse the text in the right pages
        self.collapse_content_level_text(content_level)

    def collapse_content_level(self, max_level):
        """This function marks pages with level higher than
        choosen level to be collapsed. It DOESN'T move the text."""
        for p in self.pages.values():
            if p.level > max_level:
                p.collapsed = True

    def collapse_content_level_text(self, max_level):
        """This function collapses the content
        of the pages at the choosen level. The content
        of the pages with level higher than max_level
        is moved up to the tree to the page with the max_level,
        creating titles in the page text. The pages touched
        are marked as collapsed=True."""
        for p in self.pages.values():
            if p.level == max_level:
                p.collapseSubpagesText()

    def collapse_page_level(self, max_level):
        """This function fixes the level of the pages
        in the index according to a max_level.
        Pages with a level higher than the max_level are moved
        up in the tree till the max_level. The order related
        to parent pages is mantained. The PageTree is rewrited,
        hierarchy and levels are fixed.
        Moreover the level=0 is a special level and it's content
        is moved to an intro page, because level=0 pages must
        contain the index of their subpages.
        """
        #PAGES LEVEL = 0
        #If they contain text we have to create a new page
        #called introduction (localized)
        for p in [x for x in self.pages.values() if x.level==0]:
            if len(p.text)>0:
                #creating new page for text inside text page.
                p_intro = Page(self.keywords['intro'],
                               'section',1, self.keywords)
                p_intro.text = p.text
                #saving the intro page
                self.pages[p_intro.id] = p_intro
                self.titles[p_intro.id] = p_intro.title
                p.addSubpage_top(p_intro)
                #erasing text from section page
                p.text = ''
                #fixing page references
                self.move_page_references(p, p_intro)

        #Now we move pages according to the max_level.
        #pages not collapsed and with higher level then
        #the max_level are moved as subpages of the
        #nearest max_level page.
        for p in [x for x in self.pages.values() if x.level==max_level]:
            parent_page = p.parent
            #list of subpages to move at the right level
            subpages_to_add = []
            #now we are cycling on the pages with level>max_level
            for sp in p.get_subpages():
                if not sp.collapsed:
                    #removing page from the tree acting
                    #directly on the parent page
                    sp.parent.removeSubpage(sp)
                    #saving the page for the movement
                    subpages_to_add.append(sp)
            #adding the list of moved subpages to the parent_page
            #so getting the right level.
            parent_page.addSubpages(subpages_to_add, p)
            ###NB: remember that the subpages level
            #is AUTOMATICALLY refreshed for all pages added.

    def collapse_urls(self):
        """This function creates the urls of the pages,
        checking is they are collapsed or not. If they are collapsed
        the url is parent_page#title.
        Then the references are resolved to urls throught labes"""
        self.root_page.collapseURL(self.configs['base_path'])

    def create_pagenumbers(self):
        """Every page will have a pagenumber like 1.2.1"""
        self.root_page.pagenumber = "0"
        i = 1
        for pages in self.root_page.subpages:
            pages.create_pagenumbers(None, i )
            i += 1

    def create_indexes(self, export_book_page=False):
        """This function create sections index and
        book total index"""
        self.create_sections_index()
        self.create_book_index(export_book_page=False)

    def create_sections_index(self):
        """This function create the index for the
        sections (level=0) pages"""
        for page in self.pages.values():
            if page.level == 0:
                index = []
                for p in page.get_subpages():
                    if not p.collapsed:
                        if len(p.text) >0:
                            index.append('*'*p.level+ \
                                '[[' + p.url + '|' + p.title + ']]')
                        else:
                            index.append('*'*p.level+ p.title )
                #adding section category
                index.append("<noinclude>[[Category:CourseLevelTwo]]</noinclude>")
                page.text = '\n'.join(index)


    def create_book_index(self, export_book_page=False):
        """This function create the book total index
        and the book export page index"""
        base_page = self.root_page
        #book export: link
        book_url = self.doc_title.replace(' ','_')
        #creating root index
        index = ["{{CourseRoot|"]
        if export_book_page:
            book_export_index = ['{{libro_salvato | setting-papersize = a4\
             | setting-toc = auto | setting-columns = 1}}']
            #book export: setting title
            book_export_index.append('==' + self.doc_title + '==')
        for page in self.root_page.subpages:
            if page.level == 0:
                index.append('{{CourseLevelTwo|'+page.title +'}}')
                if export_book_page:
                    #book export index for chapters
                    book_export_index.append(';' + page.title)
                    #creating index for book
                    for p in page.get_subpages():
                        if not p.collapsed:
                            if len(p.text) > 0:
                                book_export_index.append(
                                    ':[[' + p.url + '|' + p.title + ']]')
                #closing section
                index.append('\n{{ForceBreak}}\n')
        #adding course categories
        index.append("}}\n")
        index.append("[["+ self.configs["keywords"]["category"] +":Structure]]")
        index.append("<noinclude>[[Category:CourseRoot]]</noinclude>")
        base_page.text += '\n'.join(index)
        #creating book export page
        if export_book_page:
            #adding category to book page
            book_export_index.append("[["+self.configs["keywords"]["book_category"]+
                                 "|"+self.doc_title +"]]")
            book_template = self.configs["keywords"]["book_template"]
            book_title = book_template + '_' + book_url
            book_export_page = Page(book_title,
                                'root', -1,None)
            book_export_page.url = self.configs['base_path']+ \
                                book_template + '/' + self.doc_title
            #inserting index text
            book_export_page.addText(u'\n'.join(book_export_index))
            #the export book page is inserted in the pages dict and index
            self.pages[book_template + '/' + self.doc_title] = book_export_page
