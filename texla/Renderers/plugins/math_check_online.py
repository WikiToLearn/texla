import requests
import logging
from  .. import MathCheck as mc

def request_formula(tex):
    url_check = 'http://restbase.wikitolearn.org/en.wikitolearn.org/v1/media/math/check/tex'
    header= {'Accept':'application/json',
             'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'q': tex}
    r = requests.post(url_check, data=payload, headers=header)
    if r.status_code == 200:
        return True
    else:
        print("\tFormula rendering error: ", r.status_code)


def check_math(block):
    tex = block.attributes["content"]
    tex = mc.math_check(tex)
    logging.info("Plugin math_check_online @ checking formula {}".format(tex))
    request_formula(tex)

plugin_hooks = {
    'displaymath': {"pre": check_math},
    'inlinemath': {"pre": check_math},
    'ensuremath': {"pre": check_math},
    'equation': {"pre": check_math},
    'eqnarray': {"pre": check_math},
    'multline': {"pre": check_math},
    'align': {"pre": check_math},
    'alignat': {"pre": check_math}
}
