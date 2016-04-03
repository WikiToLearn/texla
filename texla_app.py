import log
import json
import logging
import os, random, string
from texla.Parser import Parser
from texla.Renderers.MediaWikiRenderer import MediaWikiRenderer
from flask import Flask, request, session, abort

dir_path = os.environ.get('TEXLA_SESSIONS_PATH','sessions')
''' Dictionary for the page_tree ready to be finalized'''
page_trees = {}

app = Flask('texla server')
app.secret_key = 'tunale_culo'


@app.route('/uploadlatex', methods=['POST'])
def upload_latex():
    '''Entrypoint for requests.
    A new session is created and latex sent saved.
    The parsing and rendering is done. Them we return
    the json structure of the pages, asking for
    collapsing levels'''
    if request.method == 'POST':
        session_id = create_session()
        logging.info('Session created @ %s',session_id)
        latex = request.form['latex']
        title = request.form['doc_title']
        session_path = os.path.join(dir_path,session_id)
        f = open(os.path.join(session_path,'text.tex'),'w')
        f.write(latex)
        f.close()
        logging.info('>>> Starting parsing')
        #starting parsing
        parser = Parser()
        block_tree = parser.parse(latex)
        #rendering
        logging.info('>>> Starting rendering')
        configs = { 'doc_title':title,
                   'output_path': session_path,
                    'keywords':'',
                    'base_path':'' }
        rend = MediaWikiRenderer(configs)
        rend.start_rendering(block_tree)
        #saving page_tree for this session
        page_trees[session_id] = rend.tree
        #creating json response
        json_tree = {}
        json_tree['json'] = rend.tree.get_tree_json()
        json_tree['session_id'] = session_id
        json_output = json.dumps(json_tree, indent=3)
        #saving trees
        f = open(os.path.join(session_path,'json_tree'),'w')
        f.write(json_output)
        f.close()
        g = open(os.path.join(session_path,'texla_tree'),'w')
        g.write(block_tree.to_json())
        g.close()
        print(page_trees)
        return json_output

@app.route('/confirmrendering/<session_id>', methods =['POST'])
def confirm_render(session_id):
    if request.method == 'POST':
        logging.info('Start post-rendering @ %s',session_id)
        if session_id in page_trees:
            page_tree = page_trees[session_id]
        else:
            abort(404)
        #getting json data
        data = json.loads(request.form['data'])
        #changing titles
        for page in data:
            page_tree.change_title(page['id'], page['title'])
        #collapsing subpages
        for page in data:
            if page['is_page']:
                page_tree.collapseSubpages(page['id'])
        #collapsing urls
        page_tree.collapseURLs()
        #now export






@app.route('/confirmrendering/sessions')
def list_page_trees():
    return str([a for a in page_trees.keys()])

def create_session():
    session_id = get_random_string(10).upper()
    os.makedirs(os.path.join(dir_path, session_id))
    return session_id

def get_random_string(N):
	return ''.join(random.SystemRandom().choice(string.ascii_lowercase + \
		string.digits) for _ in range(N))


if __name__ == '__main__':
    app.run(debug=True)
