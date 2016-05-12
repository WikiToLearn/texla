from .Page import Page
import re, os, json


class PageTree():
    def __init__(self, configs):
        self.configs = configs
        self.doc_title = configs['doc_title']
        self.keywords = configs['keywords']
        self.output_path = configs['output_path']
        #pages Data  {id: page}
        self.pages = {}
        #id : titles
        self.titles = {}
        #labels : id
        self.labels = {}
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
        self.current_id = self.root_id
        self.current_anchor = self.root_id

    def createPage(self, title, page_type):
        '''This method creates a new page and enters
        in his enviroment setting current variables'''
        #finding level
        level = len(self.pageid_stack) - 1
        #create new page
        p = Page(title, page_type, level, self.keywords)
        #add page to pages index
        self.pages[p.id] = p
        self.titles[p.id] = p.title
        #adding the page as subpage of the current page
        self.pages[self.current_id].addSubpage(p)
        #updates current
        self.pageid_stack.append(p.id)
        self.current_id = p.id
        self.current_anchor = p.id

    def exitPage(self):
        '''Return to the parent page enviroment'''
        self.current_id = self.pageid_stack[-2]
        self.pageid_stack.pop()
        self.current_anchor = self.current_id

    def addText(self, text):
        self.pages[self.current_id].addText(text)

    def addLabel(self, label):
        self.labels[label] = self.current_anchor

    def getRef(self, label):
        return self.urls[self.labels[label]]

    def get_tree_json(self):
        '''This function return the json tree'''
        return self.root_page.get_json_dictionary(self.pages)

    def get_tree_debug(self):
        '''This function prints the tree for debug'''
        s = []
        for p in self.root_page.get_subpages():
            s.append(p.get_str())
        return('\n'.join(s))

    def after_render(self):
        '''This function does some fixes after rendering'''
        for page in self.pages.values():
            page.after_render()

    def change_title(self, page_id, title):
        self.pages[page_id].title = title


    def remove_page_from_tree(self, page, parent=None):
        '''This function remove a page from the tree,
        but doesn't delete it. The page remains in the self.pages
        dictionary but not in the subpages of the pages in the tree.
        If a parent page is passed the research for the removal
        starts from that page with performance improvements'''
        if parent:
            parent.removeSubpage(page)
        else:
            self.root_page.removeSubpage(page)


    def collapse_tree(self, content_level, max_page_level):
        '''This funcion contains all the tree collapsing
        procedures in the order: subpages content collapsing,
        subpages level collapsing,
        url collapsing, fixReferences.'''
        self.collapse_content_level(content_level)
        self.collapse_page_level(max_page_level)
        self.collapse_urls()
        self.fix_references()

    def collapse_content_level(self, max_level):
        '''This functions collapse the content
        of the pages at the choosen level. The content
        of the pages with level higher than max_level
        is moved up to the tree to the page with the max_level,
        creating titles in the page text. The pages touched
        are marked as collapsed=True.'''
        for p in self.pages.values():
            if p.level == max_level:
                p.collapseSubpages()

    def collapse_page_level(self, max_level):
        '''This function fixes the level of the pages
        in the index according to a max_level.
        Pages with a level higher than the max_level are moved
        up in the tree till the max_level. The order related
        to parent pages is mantained. The PageTree is rewrited,
        hierarchy and levels are fixed.
        Moreover the level=0 is a special level and it's content
        is moved to an intro page, because level=0 pages must
        contain the index of their subpages.
        '''
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
                #we don't need to fix labels for now

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
        '''This function creates the urls of the pages,
        checking is they are collapsed or not. If they are collapsed
        the url is parent_page#title.
        Then the references are resolved to urls throught labes'''
        self.root_page.collapseURL(self.configs['base_path'])

    def fix_references(self):
        '''This function fix the references inside the
        text with the right urls instead of urls'''
        for page in self.pages.values():
            page.fixReferences(self.labels,self.pages)

    def create_indexes(self):
        '''This function create sections index and
        book total index'''
        self.create_sections_index()
        self.create_book_index()

    def create_sections_index(self):
        '''This function create the index for the
        sections (level=0) pages'''
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
                page.text = '\n'.join(index)


    def create_book_index(self):
        '''This function create the book total index
        and the book export page index'''
        base_page = self.root_page
        #book export: link
        book_url = self.doc_title.replace(' ','_')
        base_page.text+= '{{libro|Project:Libri/'+ book_url+\
                '|'+ self.doc_title + '}}\n'
        #creating root index
        index = []
        book_export_index = ['{{libro_salvato | setting-papersize = a4\
             | setting-toc = auto | setting-columns = 1}}']
        for page in self.pages.values():
            if page.level == 0:
                index.append('{{Section\n|sectionTitle=')
                index.append(page.title + '\n')
                index.append('|sectionText=\n')
                #transcluding index for section
                index.append('{{:'+ page.url+ '}}')
                #book export index for chapters
                book_export_index.append(';' + page.title)
                #creating index for book
                for p in page.get_subpages():
                    if not p.collapsed:
                        if len(p.text) > 0:
                            book_export_index.append(
                                ':[[' + p.url + '|' + p.title + ']]')
                #closing section
                index.append('}}\n{{ForceBreak}}\n')
        base_page.text += '\n'.join(index)

        #creating book export page
        #book export: setting title
        book_export_index.append('==' + self.doc_title + '==')
        book_title = 'Project:Libri_' + book_url
        book_export_page = Page(book_title,
                                'root', -1,None)
        book_export_page.url = self.configs['base_path']+ \
                                'Project:Libri/' + self.doc_title
        #inserting index text
        book_export_page.addText(u'\n'.join(book_export_index))
        #the export book page is inserted in the pages dict and index
        self.pages['Project:Libri/' + self.doc_title] = book_export_page
