# -*- coding: utf-8 -*-
import re
from ..Parser.Blocks.Utilities import *


class Page(object):
    ''' Class that manages the pages content.
    Data members of Page
    -self.id = randon id of the page
    -self.title is the title normalized for urls
    -self.title_name is the original title (could contains math)
    -self.subpages contains the list of the subpages
    -self.level memorize the level of the page.(root=-1))
    -self.url contains the unique internal url of the page
    -self.type is 'root',part,chapter,section,subsection,subsubection,paragraph.
    -self.keywords is a dictionary with localized keywords for output'''
    def __init__(self,title,title_name,url,page_type,level, keywords ):
        self.id = utility.get_random_string(5)
        self.title = title
        self.title_name = title_name
        self.url = url
        self.type = page_type
        self.keywords = keywords
        #contains the page text
        self.text = ''
        '''list of subpages urls'''
        self.subpages = []
        self.level = level
        #calculated during collapsing
        self.media_url = ''

    def addText(self,text):
        self.text = text

    def addSubpage(self, ind):
        self.subpages.append(ind)

    ''' This method insert the text of subpages in this page if his level is
    greater than the level parameter.
    It requires the dictionary of pages.'''
    def collapseText(self, ids_to_collapse ,pages_dict, subpage_index=False):
        #first of all the text is fixed
        self.fix_text_characters()
        #start collapsing
        if self.id not in ids_to_collapse:
            for subpage in self.subpages:
                pages_dict[subpage].collapseText(max_level,pages_dict)
            #the subpages'index is created if not level =-1 and if the
            #page has text
            if self.text != '':
                #added refs tags to show footnotes
                self.text+='\n<references/>'
                if subpage_index:
                    if self.subpages and self.level !=-1:
                        self.text +='\n{{noprint-pdf|\n=='+self.keywords['subpages']+'=='
                        for p in self.subpages:
                            if pages_dict[p].text != '':
                                self.text += '\n*[['+p+'|'+pages_dict[p].title_name+']]'
                        self.text+= '\n}}'
        else:
            #we have to managed the text
            for subpage in self.subpages:
                t = pages_dict[subpage].collapseText(max_level,pages_dict)
                #add text
                self.text+= '\n'+t
            if self.level ==max_level:
                #added refs tags to show footnotes
                self.text+='\n<references/>'
            elif self.level>max_level:
                #Creation of current page'title
                tit = '\n'+'='*(self.level-max_level+1)+self.title_name+'='*(self.level-max_level+1)
                self.text = tit+ "\n"+ self.text
                #return the text
                return self.text

    ''' This method collapse internal url of pages in mediawiki_url'''
    def collapseMediaURL(self,max_level,pages_dict,
                        mediaurl_dic,last_url,url_dic):
        if(self.level<max_level):
            last_url = self.url
            #saving mediaurl
            mediaurl_dic[self.url] = self.media_url = self.url
            #managing subspace
            for subpage in self.subpages:
                pages_dict[subpage].collapseMediaURL(
                    max_level,pages_dict,\
                    mediaurl_dic,last_url,url_dic)
        else:
            if self.level==max_level:
                last_url = self.url
                #saving mediawikiurl
                self.media_url= self.url
                mediaurl_dic[self.url] = self.media_url
            else:
                #creation of media-wiki url
                murl = last_url+'#'+self.title
                if murl in url_dic:
                    nused = url_dic[murl]
                    murl+= '_'+str(nused+1)
                    url_dic[murl]+=1
                #saving mediawiki url
                self.media_url= murl
                mediaurl_dic[self.url]=murl
            #managing subpages
            for subpage in self.subpages:
                pages_dict[subpage].collapseMediaURL(
                    max_level, pages_dict,
                    mediaurl_dic,last_url,url_dic)


    '''This method insert the right mediawikiurl in
    the \ref tags after the collapsing'''
    def fixReferences(self, labels, pages):
        for label in re.findall(r'\\ref{(.*?)}', self.text):
            #convert label to int
            try:
                label_n = int(label)
                if label_n == -1:
                    #ref not foung
                    self.text = self.text.replace('\\ref{'+label+'}',
                            "'''MISSING REF'''")
                    continue
                page = pages[labels[label_n]]
                if page.url != self.url:
                    self.text = self.text.replace('\\ref{'+label+'}',\
                        ' ([[' + page.url + '|'+ page.title_name + ']]) ')
                else:
                    self.text = self.text.replace('\\ref{'+label+'}',' ')
            except Exception:
                print("REF_ERROR: "+ label)

    def get_json_dictionary(self, pages):
        '''This function return the json dictionary of the page
        with all its children'''
        s = {}
        s['ID'] = self.id
        s['title'] = self.title
        s['level'] = self.level
        s['text'] = self.text
        s['children'] = []
        for page in self.subpages:
            s['children'].append(pages[
                page].get_json_dictionary(pages))
        return s


    def __str__(self):
        s =[]
        s.append('title='+self.title)
        s.append('title_name='+self.title_name)
        s.append('url='+self.url)
        s.append('media_url='+ self.media_url)
        s.append('subpages='+str(self.subpages))
        s.append('level='+str(self.level))
        return '  '.join(s)
