import requests
import logging
from multiprocessing import Process, Pool, Queue

def request_formula(tex):
    url_check = 'http://restbase.wikitolearn.org/pool.wikitolearn.org/v1/media/math/check/tex'
    header= {'Accept':'application/json',
             'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'q': tex}
    r = requests.post(url_check, data=payload, headers=header)
    if r.status_code == 200:
        return True
    else:
        return False

formulas = []
bad_formulas = Queue()

def save_math(block):
    tex = block.attributes["content"]
    #saving the formula only if it's longer than 10
    if len(tex)>10:
        logging.debug("Plugin math_check_online @ saving formula {}".format(tex))
        formulas.append((tex, block.id))

def save_math_align(block):
    tex = "\\begin{align}" + block.attributes["content"] + "\\end{align}"
    #saving the formula only if it's longer than 10
    if len(tex)>50:
        logging.debug("Plugin math_check_online @ saving formula {}".format(tex))
        formulas.append((tex, block.id))

def check_math(formula):
    ok = request_formula(formula[0])
    if ok:
        logging.info("Plugin math_check_online @ formula {}, block_id: {}".format("OK", formula[1]))
    else:
        logging.error("Plugin math_check_online @ formula {}, block_id: {}".format("BAD", formula[1]))
        bad_formulas.put(formula[1]+": "+formula[0])

def start_pool():
    pool = Pool(processes=6)
    logging.info("Plugin math_check_online @ total formulas to check: {}".format(len(formulas)))
    pool.map(check_math, formulas)
    #saving results
    with open("math_errors.txt","w") as f:
        while not bad_formulas.empty():
            form = bad_formulas.get()
            f.write(form + "\n\n")



def start_check():
    p = Process(target=start_pool)
    p.start()


plugin_render_hooks = {
    'displaymath': {"pre": save_math},
    'inlinemath': {"pre": save_math},
    'ensuremath': {"pre": save_math},
    'equation': {"pre": save_math},
    'eqnarray': {"pre": save_math_align},
    'multline': {"pre": save_math_align},
    'align': {"pre": save_math_align},
    'alignat': {"pre": save_math_align}
}

plugin_lifecycle_hooks = {
    "end" : start_check
}
