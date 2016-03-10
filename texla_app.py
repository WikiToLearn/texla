from flask import Flask
from texla.Parser import Parser
# from texla.Renderers.MediaWikiRenderer import MediaWikiRenderer

app = Flask(__name__)


@app.route('/putlatex')
def put_latex():
    print('ciao')
    # if request.method == 'POST':
    #     pass
    #     # latex = request.form['latex']
    #     # p = Parser()
    #     # tree = p.parse(latex)
    #     # #rendering
    #     # rend = MediaWikiRenderer({'doc_title':'Prova','output_path':"test.mw",
    #     #                         'keywords':'', 'base_path':''})
    #     # rend.start_rendering(tree)
    #     # session['pagetree'] = rend.tree
    #     # return rend.tree.get_tree_json()


if __name__ == '__main__':
    app.debug = True
    app.run()
