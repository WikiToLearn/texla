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
        return self.pages[self.root_id].get_json_dictionary(self.pages)

    def after_render(self):
        '''This function does some fixes after rendering'''
        for page in self.pages.values():
            page.after_render()

    def change_title(self, page_id, title):
        self.pages[page_id].title = title


    def collapse_tree(self, level):
        '''This funcion contains all the tree collapsing
        procedures in the order: subpages collapsing,
        url collapsing, fixReferences.'''
        self.collapseSubpages(level)
        self.collapseURLs()
        self.fixReferences()

    def collapseSubpages(self, level):
        ''' All the pages with the right level are collapsed'''
        for p in self.pages.values():
            if p.level == level:
                p.collapseSubpages()
        #now we have to fix the pages with higher level
        #PAGES LEVEL = 0
        #If they contain text we have to create a new page
        #called introduction (localized)
        pages_to_add = []
        for p in self.pages.values():
            if p.level == 0:
                if len(p.text)>0:
                    p_intro = Page(self.keywords['intro'],
                                   'section',1, self.keywords)
                    p_intro.text = p.text
                    pages_to_add.append(p_intro)
                    self.titles[p_intro.id] = p_intro.title
                    p.addSubpage_top(p_intro)
                    #erasing text from section page
                    p.text = ''
                    #we don't need to fix labels for now
        #adding all introduction pages
        for p in pages_to_add:
            self.pages[p.id] = p

    def collapseURLs(self):
        '''This function creates the urls of the pages,
        checking is they are collapsed or not. If they are collapsed
        the url is parent_page#title.
        Then the references are resolved to urls throught labes'''
        self.pages[self.root_id].collapseURL(self.configs['base_path'])

    def fixReferences(self):
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
        base_page = self.pages[self.root_id]
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
