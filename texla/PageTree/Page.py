# -*- coding: utf-8 -*-
import re
import logging
from ..Parser.Blocks.Utilities import *


class Page():
    ''' Class that manages the pages content.
    Data members of Page
    -self.id = randon id of the page
    -self.title is the title normalized for urls
    -self.subpages contains the list of the subpages objects
    -self.level memorize the level of the page.(root=-1))
    -self.url contains the unique internal url of the page
    -self.type is 'root',part,chapter,section,subsection,subsubection,paragraph.
    -self.keywords is a dictionary with localized keywords for output'''
    def __init__(self,title, page_type, level, keywords ):
        self.id = utility.get_random_string(8)
        self.title = title
        self.type = page_type
        self.keywords = keywords
        #contains the page text
        self.text = ''
        self.collapsed = False
        '''list of subpages urls'''
        self.subpages = []
        self.level = level

    def addText(self,text):
        self.text = text

    def addSubpage(self, page):
        self.subpages.append(page)

    def after_render(self):
        '''This function does some fixes after rendering'''
        #check math inside titles
        self.math_inside_title = self.is_math_inside_title()

    def collapseSubpages(self, level=0):
        ''' This method insert the text of subpages in this
        page and returns the complete text.
        It requires the dictionary of pages.'''
        #first of all the text is fixed
        self.fix_text_characters()
        #start collapsing
        #we have to managed the text
        for subpage in self.subpages:
            t = subpage.collapseSubpages(level+1)
            #add text
            self.text+= '\n'+t
        if level == 0:
            if '<ref>' in self.text:
                #added refs tags to show footnotes
                self.text+='\n<references/>'
        else:
            #Creation of current page'title
            tit = '\n'+'='*(level)+self.title+ \
                    '='*(level)
            self.text = tit+ "\n"+ self.text
            #marking as collapsed
            self.collapsed = True
            #return the text
            return self.text

    def collapseURL(self, base_url):
        '''This functions creates the url of the page
        checking if it is collapsed'''
        if self.collapsed:
            self.url = base_url + '#' + self.title
            for p in self.subpages:
                p.collapseURL(base_url)
        else:
            self.url = base_url + '/' + self.title
            for p in self.subpages:
                p.collapseURL(self.url)

    def fixReferences(self, labels, pages):
        '''This method insert the right mediawikiurl in
        the \ref tags after the collapsing'''
        for label in re.findall(r'\\ref{(.*?)}', self.text):
            #convert label to int
            try:
                page = pages[labels[label]]
                if page.url != self.url:
                    self.text = self.text.replace('\\ref{'+label+'}',\
                        ' ([[' + page.url + '|'+ page.title + ']]) ')
                else:
                    self.text = self.text.replace('\\ref{'+label+'}',' ')
            except Exception:
                self.text = self.text.replace('\\ref{'+label+'}',
                                        "''MISSING REF'''")
                logging.error("REF_ERROR: "+ label)

    def fix_text_characters(self):
        '''Utility function to fix apostrophes and other characters
        inside the text of the page'''
        #fix for double apostrophes quotes
        s = re.findall(u'(\`\`)\s?(.*?)\s?(\'\')', self.text, re.DOTALL)
        for item in s:
            self.text = self.text.replace(item[0],'"')
            self.text = self.text.replace(item[2],'"')
        s2 = re.findall(u'(\‘\‘)\s?(.*?)\s?(\’\’)', self.text, re.DOTALL)
        for item2 in s2:
            self.text = self.text.replace(item2[0],'"')
            self.text = self.text.replace(item2[2],'"')
        #apostrophe fixed
        self.text = self.text.replace(u'’',u"'")
        self.text = self.text.replace(u'`',u"'")

    def is_math_inside_title(self):
        '''This function checkes if there is math inside titles'''
        mre = re.search(r'(?<![\$])\$([^$]+)\$(?!\$)|'+
                        r'(?<![\$])\$\$([^$]+)\$\$(?!\$)|'+
                        r'\\\((.*?)\\\)|\\\[(.*?)\\\]',
                        self.title,re.DOTALL)
        if mre:
            return True
        else:
            return False

    def get_json_dictionary(self, pages):
        '''This function return the json dictionary of the page
        with all its children'''
        s = {}
        s['ID'] = self.id
        s['title'] = self.title
        s['level'] = self.level
        if self.level>2:
            s['is_page'] = False
        else:
            s['is_page'] = True
        s['text'] = self.text
        s['children'] = []
        for page in self.subpages:
            s['children'].append(page.get_json_dictionary(pages))
        return s


    def __str__(self):
        s =[]
        s.append('title='+self.title)
        s.append('url='+self.url)
        s.append('subpages='+str(self.subpages))
        s.append('level='+str(self.level))
        return '  '.join(s)
