texla
=====

![](doc/texla-logo.png)

A minimal and easily extensible LaTeX parser.

It's **minimal** because it only splits tex without doing anything strange to the sources.
It breaks down LaTeX into sections, environments, math, commands and plain text, creating a
simple tree of Blocks objects.

It's **easily extensible** because to support a new command or environment the only necessary code is a
Python class that defines a new Block. Moreover options and arguments of Latex commands and environments could be parsed with a simple and easy **API**.

Further documentation can be found at: https://meta.wikitolearn.org/Texla

Run Texla
=========
To run Texla you'll need Python3 and PyYaml installed.

    python texla.py
    python texla.py --debug

Texla Configuration
===================

The execution of texla is controlled by the **configs.yaml** file.

There are a few parameters to set:

* __renderer__ : The output format of the conversion. __mediawiki__ is the only avaiable one for now

* __input_path__ : the path of the main tex file to convert. Texla is able to convert complex documents with many included subfiles: in "input_path" you have to put the main tex file that includes all the subfiles.

* __output_path__ : the path for the output files. Write it without the extension because it will be the base filename for all output files.

* __doc_title__: The title of the document. Texla doesn't read the title written inside tex. :__doc_title__ is used as a base namespace for pages

* __base_path__: texla exports pages in an hierarchical way, organizing pages with unique urls. __base_path__ is used as a root for the urls of the pages. It can be void.

* __collapse_content_level__ : The sectioning of a latex file is a tree. Every part of the tex doc has a level. The level of the root page, that contains the index of the document is -1. The first level of sectioning in the document has level 0. Texla converts the sections into pages and the page gets the level of the seciton. The content of the pages with level greater than __collapse_content_level__ is inserted in the text of the parent page as a paragraph.

* __collapse_pages_level__: If a page has a level greater than __collape_pages_level__ and is not collapsed, it is moved to the level given by __collapse_pages_level__ going up in the page tree.

* __create_index__: if True a index is create in the root page.

* __export_format__ : for now _text_ is the only avaiable

* __export_single_pages__: if True a file for every page is created and saved in a directory called __"output_path"_pages__

* __export_pages_tree__: if True the pages are exported in a tree of directory (root in __"output_path"_pages__ ) corresponding to the actual sectioning.

* __export_book_page__: If True the page necessary to Project:Books is created.

* __print_preparsed_tex__: if True a debug file called _preparsed.tex_ is saved with preparsed tex.

* __lang__: localization for keywords. The avaiable languages are those inside __i18n.yaml__ file. Contributions appreciated :)

* __plugins__: [...]  List of the enabled plugins. The order of this list is the order of executing: Be Careful.

* __plugins_configs__: yaml dictionary containing the key-value configuration for each plugin (see configs_example.yaml)


Plugins
=======
The available plugins are:

* __MathCheck__: it fixes the math to be correct for WikiToLearn rendering

* __math_check_online__: at the end of the rendering it calls the WikiToLearn math renderer to check if there are errors in the math.

* __space_check__: it removes the single spaces after a newline.
