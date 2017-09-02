# -*- coding: utf-8 -*-
import re
import logging
from ..Parser.Utilities import *


class Page():
    """ Class that manages the pages content.
    Data members of Page
    -self.id = randon id of the page
    -self.title is the title normalized for urls
    -self.subpages contains the list of the subpages objects
    -self.level memorize the level of the page.(root=-1))
    -self.url contains the unique internal url of the page
    -self.type is 'root',part,chapter,section,subsection,subsubection,paragraph.
    -self.keywords is a dictionary with localized keywords for output"""
    def __init__(self,title, page_type, level, keywords ):
        self.id = utility.get_random_string(8)
        self.title = title
        self.type = page_type
        self.keywords = keywords
        #contains the page text
        self.text = ''
        self.collapsed = False
        #list of subpages objects
        self.subpages = []
        self.parent = None
        self.level = level

    def addText(self,text):
        self.text = text.strip()

    def addSubpage(self, page, after=None):
        """This methods add a subpage
        refreshing the levels of ALL subpages.
        It sets also the parent of the subpage"""
        if after:
            i = self.subpages.index(after)
            self.subpages.insert(i+1, page)
        else:
            self.subpages.append(page)
        #setting level
        page.refresh_level(self.level+1)
        #setting parent
        page.parent = self

    def addSubpages(self, pages, after=None):
        """This function add a list of subpages,
        setting levels and parent page."""
        if after:
            i = self.subpages.index(after) +1
            self.subpages = self.subpages[:i] + pages +\
                            self.subpages[i:]
        else:
            self.subpages += pages
        #setting level and parent of subpages
        for p in pages:
            p.refresh_level(self.level+1)
            p.parent = self

    def addSubpage_top(self, page):
        """This function add a subpage before all the others."""
        self.subpages.insert(0,page)
        page.parent = self

    def removeSubpage(self, page):
        """This function removes the subpage
        recursively looking also at subpages"""
        if page in self.subpages:
            self.subpages.remove(page)
            page.parent = None
        else:
            for p in self.subpages:
                p.removeSubpage(page)

    def isSubpage(self,page):
        return page in self.subpages

    def get_subpages(self):
        """This function returns a list with all the subpages
        of the current page walking the subtree
        KEEPING THE ORDER (REALLY IMPORTANT):
        -subpage:
            --subsub1
            --subsub2:
                ---subsubsub
        -subpage2...
        => [subpage, subsub1, subsub2, subsubsub, subpage2, ...]"""
        subpag = []
        for p in self.subpages:
            subpag.append(p)
            subpag += p.get_subpages()
        return subpag

    def refresh_level(self, new_level):
        """This function change the level of this page
        refreshing recursively all the subpages"""
        self.level = new_level
        for p in self.subpages:
            p.refresh_level(self.level+1)

    def after_render(self):
        """This function does some fixes after rendering"""
        #first of all the text is fixed
        self.fix_text_characters()
        #check math inside titles
        self.math_inside_title = self.is_math_inside_title()


    def collapseSubpagesText(self, level=0):
        """ This method insert the text of subpages in this
        page and returns the complete text."""
        for subpage in self.subpages:
            t = subpage.collapseSubpagesText(level+1)
            #add text
            self.text+= '\n'+t
        if level == 0:
            if '<ref>' in self.text:
                #added refs tags to show footnotes
                self.text+='\n{{Notes}}'
        else:
            #Creation of current page title
            tit = '\n'+'='+'='*(level)+self.title+ \
                    '='*(level)+'='
            self.text = tit+ "\n"+ self.text
            #return the text
            return self.text


    def collapseURL(self, base_url):
        """This functions creates the url of the page
        checking if it is collapsed. Then it continues
        with the subpages"""
        if self.collapsed:
            self.url = base_url + '#' + self.title
            for p in self.subpages:
                p.collapseURL(base_url)
        else:
            if base_url != '':
                self.url = base_url + '/' + self.title
            else:
                self.url = self.title
            for p in self.subpages:
                p.collapseURL(self.url)

    def create_pagenumbers(self, parent, current):
        """This function creates the pagenumber string appending to the
        parent number its position in the pages of the same level. Then
        the process continues with subpages"""
        if parent != None:
            self.pagenumber = parent+ ".{}".format(current)
        else:
            self.pagenumber = str(current)
        i = 1
        for page in self.subpages:
            page.create_pagenumbers(self.pagenumber, i)
            i += 1

    def fix_text_characters(self):
        """Utility function to fix apostrophes and other characters
        inside the text of the page"""
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
        """This function checkes if there is math inside titles"""
        mre = re.search(r'(?<![\$])\$([^$]+)\$(?!\$)|'+
                        r'(?<![\$])\$\$([^$]+)\$\$(?!\$)|'+
                        r'\\\((.*?)\\\)|\\\[(.*?)\\\]',
                        self.title,re.DOTALL)
        if mre:
            return True
        else:
            return False

    def get_json_dictionary(self, pages):
        """This function return the json dictionary of the page
        with all its children"""
        s = {}
        s['ID'] = self.id
        s['title'] = self.title
        s['level'] = self.level
        s['collapsed'] = self.collapsed
        if self.level>2:
            s['is_page'] = False
        else:
            s['is_page'] = True
        s['text'] = self.text[:100]
        s['children'] = []
        for page in self.subpages:
            s['children'].append(page.get_json_dictionary(pages))
        return s

    def get_str(self):
        a = '  [C]' if self.collapsed else ''
        return '('+ str(self.level)+')'+'---'*self.level +\
                '> '+ self.title + a


    def __str__(self):
        s =[]
        s.append('title="'+self.title+'"')
        if hasattr(self, "url"):
            s.append('url="'+self.url + '"')
        s.append('subpages='+str(len(self.subpages)))
        s.append('level='+str(self.level))
        s.append('collapsed='+ str(self.collapsed))
        return '  '.join(s)
