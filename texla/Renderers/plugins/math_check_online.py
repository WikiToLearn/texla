import requests
import logging
from multiprocessing import Process, Pool, Queue
from os import path


def request_formula(tex):
    url_check = 'http://restbase.{0}/pool.{0}/v1/media/math/check/tex'.format(configs["domain"])
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
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
    if len(tex) > 5:
        logging.debug("Plugin math_check_online @ saving formula {}".format(
            tex))
        formulas.append((tex, block.id))


def save_math_align(block):
    tex = "\\begin{align}" + block.attributes["content"] + "\\end{align}"
    #saving the formula only if it's longer than 10
    if len(tex) > 50:
        logging.debug("Plugin math_check_online @ saving formula {}".format(
            tex))
        formulas.append((tex, block.id))


def check_math(formula):
    ok = request_formula(formula[0])
    if ok:
        logging.info("Plugin math_check_online @ formula {}, block_id: {}".
                     format("OK", formula[1]))
    else:
        logging.error("Plugin math_check_online @ formula {}, block_id: {}".
                      format("BAD", formula[1]))
        bad_formulas.put(formula)


def start_pool():
    pool = Pool(processes=int(configs["threads"]))
    logging.info("Plugin math_check_online @ total formulas to check: {}".
                 format(len(formulas)))
    pool.map(check_math, formulas)
    #saving results
    logging.info("GOOD FORMULAS: {}  --- BAD FORMULAS: {}".format(
        len(formulas)-bad_formulas.qsize(), bad_formulas.qsize()))
    log_matherrors_file_path = path.relpath("debug/math_errors.txt")
    with open(log_matherrors_file_path, "w") as f:
        f.write("Math Errors Tree Log: \n")
        f.write("---------------------\n")
        ids = []
        while not bad_formulas.empty():
            form = bad_formulas.get()
            ids.append(form[1])
        output = tree_explorer.print_tree_to_blocks(ids)
        f.write(output + "\n\n")


def start_check():
    p = Process(target=start_pool)
    p.start()


plugin_render_hooks = {
    'displaymath': {
        "pre": save_math
    },
    'inlinemath': {
        "pre": save_math
    },
    'ensuremath': {
        "pre": save_math
    },
    'equation': {
        "pre": save_math
    },
    'eqnarray': {
        "pre": save_math_align
    },
    'multline': {
        "pre": save_math_align
    },
    'align': {
        "pre": save_math_align
    },
    'alignat': {
        "pre": save_math_align
    }
}

plugin_lifecycle_hooks = {"end": start_check}

needs_tree_explorer = True
tree_explorer = None
configs = {}
