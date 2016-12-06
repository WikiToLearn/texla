import logging

class TheoremsManager:

    def __init__(self):
        self.pages_ths = {}

    def addTheorem(self, theorem):
        page = theorem.page
        if page not in self.pages_ths:
            self.pages_ths[page] = []
        self.pages_ths[page].append(theorem)

    def fix_theorems(self):
        #first of all we have to recover the right pages
        #checking the collapsing
        for page in self.pages_ths:
            current_page = page
            while(True):
                if current_page.collapsed:
                    current_page = current_page.parent
                else:
                    break
            #so now the theorems of page belong to current_page
            i = 1
            for th in self.pages_ths[page]:
                th.fixNumber(current_page.pagenumber + ".{}".format(i))
                th.fixUrl(current_page)
                i += 1


class Theorem:

    def __init__(self, id, page, th_type):
        self.id = id
        self.page = page
        self.th_type = th_type
        self.number = 0

    def fixNumber(self, number):
        '''This method fix the number of the theorem
        inside its page text replacing the string {{thnum:id}}.
        The number is also appended to the title'''
        self.page.text = self.page.text.replace("{{thnum:"+ self.id + "}}", str(number))
        #creating title for label management
        self.title = self.th_type + " " + str(number)
        self.number = number

    def fixUrl(self, basepage):
        '''The theorem url is setted to the page url.
        N.B.: to be called after pages' urls fixing'''
        self.url = self.page.url

    def __str__(self):
        return "Theorem. Type: {}, Page: {} Number: {}".format(
            self.th_type, self.page.title, self.number )
