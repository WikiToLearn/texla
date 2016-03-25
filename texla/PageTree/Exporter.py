from .Page import *
import os
'''Entry point for exporting pages. config is a tuple
with (export_format, username, userid)'''


def exportPages(pages, path, format):
    #choosing format
    f = open(path, 'w')
    if format == 'text':
        f.write(exportText(pages))
    f.close()


def export_singlePages(pages, base_path, format):
    '''Entry point to export pages in separated files.'''
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    if format == 'text':
        exportText_single_pages(pages, base_path)


def exportText(pages):
    '''Functions that exports all the pages in our file with
    format usable with pagefromfile.py script'''
    output = []
    for page in pages.values():
        if not page.collapsed:
            if page.text != "":
                output.append('##########')
                output.append('\'\'\'' + page.url + '\'\'\'')
                output.append(page.text)
                output.append('@@@@@@@@@@')
    return '\n'.join(output)


def exportText_single_pages(pages, base_path=''):
    '''Function that exports the text of
    pages in separated files'''
    pf = open(base_path + '/pages.txt', 'w')
    for page in pages.values():
        pf.write('# [[' + page.url + ']]\n')
        if not page.collapsed:
            if page.text != "":
                text = []
                text.append('##########')
                text.append('\'\'\'' + page.url + '\'\'\'')
                text.append(page.text)
                text.append('@@@@@@@@@@')
                path = base_path + '/' + page.title + ".txt"
                path = path.encode('utf-8')
                f = open(path, 'w')
                f.write('\n'.join(text))
                f.close()
    pf.close()
