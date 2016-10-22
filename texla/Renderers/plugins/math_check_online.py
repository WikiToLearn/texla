import requests
import logging

def request_formula(tex):
    url_check = 'http://restbase.wikitolearn.org/en.wikitolearn.org/v1/media/math/check/tex'
    header= {'Accept':'application/json',
             'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'q': tex}
    r = requests.post(url_check, data=payload, headers=header)
    if r.status_code == 200:
        return True
    else:
        return False

formulas = []


def save_math(block):
    tex = block.attributes["content"]
    logging.debug("Plugin math_check_online @ saving formula {}".format(tex))
    formulas.append(tex)

def check_math():
    w = open("math_errors.txt",'w')
    i = 0
    tot = len(formulas)
    for f in formulas:
        ok = request_formula(f)
        if ok:
            logging.info("Plugin math_check_online @ formula {}/{} {}".format(i, tot, "OK"))
        else:
            logging.error("Plugin math_check_online @ formula {}/{} {}".format(i, tot, "BAD"))
        i += 1
        w.write(f + "\n\n")
    w.close()


plugin_render_hooks = {
    'displaymath': {"pre": save_math},
    'inlinemath': {"pre": save_math},
    'ensuremath': {"pre": save_math},
    'equation': {"pre": save_math},
    'eqnarray': {"pre": save_math},
    'multline': {"pre": save_math},
    'align': {"pre": save_math},
    'alignat': {"pre": save_math}
}

plugin_lifecycle_hooks = {
    "end" : check_math
}
