import log
import logging
import os, random, string
from texla.Parser import Parser
from texla.Renderers.MediaWikiRenderer import MediaWikiRenderer
from flask import Flask, request, session

dir_path = os.environ.get('TEXLA_SESSIONS_PATH','sessions')

app = Flask('texla server')
app.secret_key = 'tunale_culo'


@app.route('/uploadlatex', methods=['POST'])
def upload_latex():
    if request.method == 'POST':
        session_id = create_session()
        logging.info('Session created @ %s',session_id)
        latex = request.form['latex']
        title = request.form['doc_title']
        session_path = os.path.join(dir_path,session_id)
        f = open(os.path.join(session_path,'text.tex'),'w')
        f.write(latex)
        f.close()
        #starting parsing
        parser = Parser()
        block_tree = parser.parse(latex)
        #rendering
        configs = { 'doc_title':title,
                   'output_path': session_path,
                    'keywords':'',
                    'base_path':'' }
        rend = MediaWikiRenderer(configs)
        rend.start_rendering(block_tree)
        json_tree = rend.tree.get_tree_json()
        #saving trees
        f = open(os.path.join(session_path,'json_tree'),'w')
        f.write(json_tree)
        f.close()
        g = open(os.path.join(session_path,'texla_tree'),'w')
        g.write(block_tree.to_json())
        g.close()
        return json_tree


def create_session():
    session_id = get_random_string(10).upper()
    os.makedirs(os.path.join(dir_path, session_id))
    return session_id

def get_random_string(N):
	return ''.join(random.SystemRandom().choice(string.ascii_lowercase + \
		string.digits) for _ in range(N))


if __name__ == '__main__':
    app.run(debug=True)
