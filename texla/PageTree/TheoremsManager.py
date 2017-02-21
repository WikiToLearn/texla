import logging

class TheoremsManager:

    def __init__(self, pages_dict):
        #refernce to the pages dictionary
        self.pages = pages_dict
        self.pages_ths = {}

    def addTheorem(self, theorem):
        page = theorem.page
        logging.debug("TheoremsManager @ adding Theorem: {}".format(theorem))
        if page not in self.pages_ths:
            self.pages_ths[page] = []
        self.pages_ths[page].append(theorem)

    def move_theorems_page(self, oldpage, newpage):
        """This function moves a theorem to a different page
        to maintain the right anchor in case of moved page."""
        if oldpage in self.pages_ths:
            self.pages_ths[newpage] = self.pages_ths[oldpage]
            self.pages_ths.pop(oldpage)


    def fix_theorems(self):
        """This function fixes the theorems calculating their
        number and substituing it the placeholder in the text.
        Moreover it fixes the data needed by the label manager."""
        for chapter in [x for x in self.pages.values() if x.level == 0]:
            chapter_number = chapter.pagenumber
            th_numbering = {}
            pages_to_check = self.get_subpages_ordered(chapter)
            for pag in pages_to_check:
                for th in self.pages_ths[pag]:
                    if th.th_type in th_numbering:
                        number = th_numbering[th.th_type] +1
                    else:
                        number = 1
                        th_numbering[th.th_type] = 1
                    th_numbering[th.th_type] = number
                    th.fixNumber(chapter_number+"."+str(number))
                    th.fixUrl()

    def get_subpages_ordered(self, page):
        pages = []
        for subp in page.subpages:
            if subp in self.pages_ths:
                pages.append(subp)
            pages += self.get_subpages_ordered(subp)
        return pages


class Theorem:

    def __init__(self, id, page, th_type):
        self.id = id
        self.page = page
        #creating a text value. If the Theorem is used
        #as reference the text of the parent page is used.
        self.text = page.text
        self.th_type = th_type
        self.number = 0
        self.title = None
        self.url = None

    def fixNumber(self, number):
        """This method fix the number of the theorem
        inside its page text replacing the string {{thnum:id}}.
        The number is also appended to the title"""
        self.page.text = self.page.text.replace(
                "{{thnum@"+ self.id + "}}", str(number))
        #creating title for label management. Only the number as latex.
        self.title = str(number)
        self.number = number
        logging.debug("Theorem @ Fixing number {} of theorem: {}".
                      format(number, self))

    def fixUrl(self):
        """The theorem url is setted to the page url.
        N.B.: to be called after pages' urls fixing"""
        #getting not collapsed url
        current_page = self.page
        while True:
            if current_page.collapsed:
                current_page = current_page.parent
            else:
                break
        self.url = current_page.url + "#" + self.th_type + self.title.replace(".", "_")
        #replacing anchor in the text
        self.page.text = self.page.text.replace(
                "{{thanchor@"+ self.id + "}}", self.th_type + self.title.replace(".","_"))
        logging.debug("Theorem @ Fixing URL of theorem {}".format(self))

    def __str__(self):
        return "Theorem. ID: {}. Type: {}, Page: {}, Number: {}".format(
            self.id, self.th_type, self.page.title, self.number )
