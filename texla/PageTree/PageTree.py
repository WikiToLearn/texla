from .Page import Page
import re, os, json

class PageTree():

    def __init__(self, configs):
        self.configs = configs
        self.doc_title= configs['doc_title']
        self.keywords = configs['keywords']
        self.output_path = configs['output_path']
        #pages Data
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
        level = len(self.pageid_stack)-1
        #create new page
        p = Page(title, page_type,level,self.keywords)
        #add page to pages index
        self.pages[p.id] = p
        self.titles[p.id] = p
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
        return json.dumps(self.pages[
            self.root_id].get_json_dictionary(self.pages),
            indent=3)

    def after_render(self):
        '''This function does some fixes after rendering'''
        for page in self.pages.values():
            page.after_render()

    def collapseSubpages(self, pages_to_collpase, subpages_index):
        ''' This method collapse the text contained in subpages
        in the pages marked in pages_to_collapse.'''
        for page in pages_to_collapse:
            page.collapseText()

    def collpaseURLs(self):
        '''This function collpases the urls of the pages'''
        self.pages[self.root_id].collpaseURL(
                        configs['base_path'])

    def fixReferences(self):
        for page in self.pages.values():
            page.fixReferences(self.labels,self.pages)

    '''index for book export page'''
    book_export_index = ['{{libro_salvato | setting-papersize = a4\
                 | setting-toc = auto | setting-columns = 1}}']


    '''Method that creates the index in the root page and the
    index for book export page'''
    def createIndex(self,max_level):
        ind = ''
        base_page = self.pages[self.root_id]
        base_page.text += '{{RiferimentiEsterni \
        |esercizi= \n|dispense=\n|testi=}}\n'
        #book export: link
        base_page.text+= '{{libro|Project:Libri/'+self.doc_title+\
                '|'+ self.doc_title + '}}\n'
        #book export: setting title
        self.book_export_index.append('=='+ self.doc_title+'==')
        #creating root index
        base_page.text+= '\n\n==' +self.keywords['chapters']+'==\n'
        base_page.text+= self._createIndex(self.pages[self.root_id],
                        '',max_level)
        #creating book export page
        book_title = 'Project:Libri_'+self.doc_title
        book_export_page= Page(book_title,book_title,
            'Project:Libri/'+self.doc_title,'root',-1,None)
        #inserting index text
        book_export_page.addText(u'\n'.join(self.book_export_index))
        #the export book page is inserted in the pages dict and index
        self.pages['Project:Libri/'+self.doc_title] = book_export_page

    def _createIndex(self,page,ind,max_level):
        index = []
        for p in page.subpages:
            #managing chapters
            if p.level ==0:
                index.append('{{Section\n|sectionTitle=')
                index.append(p.title+'\n')
                index.append('|sectionText=\n')
                #book export index for chapters
                self.book_export_index.append(';'+ p.title)
                if p.text != '':
                    index.append('*[['+ p.url+'|'+\
                                    self.keywords['intro']+ ']]\n')
                    self.book_export_index.append(':[['+ p.url+']]')

            elif p.text !='':
                index.append(ind+'[['+ p.url+'|'+ p.title+']]\n')
                self.book_export_index.append(':[['+ p.url+']]')
            else:
                index.append(ind + p.title + '\n')
            #next level
            if(self.pages[page].level<max_level-1):
                index.append(self._createIndex(p ,ind+'*',max_level))
            #closing chapter
            if p.level==0:
                index.append('}}\n{{ForceBreak}}\n')
        return u''.join(index)








pass
