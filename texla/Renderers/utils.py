### UTILITY FUNCTIONS ###
from string import *
import re, json
from ..Parser.Utilities import EnvironmentParser


def remove_command_greedy(tex, command, delete_content=False):
    '''This function remove a command like
    \command[simple option]{content} even if it contains
    nested brakets. If delete_content=False it leaves
    the content of the command without the command,
    otherwise it deletes all. The options are removed'''
    while(True):
        r = re.search(r'\\' + command +'(\[.*?\])*(?=[\s\{\[])', tex)
        result = ''
        if r:
            left = tex[:r.start()]
            right = tex[r.end():].lstrip()
            result = left
            #getting content
            level = 0
            pos = -1
            for ch in right:
                pos += 1
                if ch == '{':
                    level += 1
                elif ch == '}':
                    level -= 1
                #now check if we are returned to 0 level
                if level == 0:
                    add_space = (pos+1)==len(right) or right[pos+1] not in ["\\", " "]
                    if not delete_content:
                        if add_space:
                            result += right[1:pos]+ " " +right[pos+1:]
                        else:
                            result += right[1:pos] +right[pos+1:]
                    else:
                        if add_space:
                            result +=  " " + right[pos + 1:]
                        else:
                            result +=  right[pos + 1:]
                    break
            tex = result
            #new cycle
        else:
            #no match, end of cycle
            return tex

def remove_command_no_options(tex, command):
    '''This funcion removes simply a command,
    checking if is followed by space or another command'''
    r = re.compile(r'\\'+command +r'(?![a-zA-Z])')
    return r.sub('', tex)


def replace_command_greedy(tex,
                           command,
                           repl,
                           rm_content=False,
                           left_delim='{',
                           right_delim='}',
                           rm_slash=False):

    ''' This function replace a command with the
    repl par. It MUST be used with command with {},
    not with declaration. It understands nested brakets.
    If rm_content is true che content of the command
    and {} are removed'''
    while(True):
        r = re.search(r'\\' + command +'(\[.*?\])*(?=[\s\{\[])', tex)
        result = ''
        if r:
            left = tex[:r.start()]
            right = tex[r.end():].lstrip()
            result = left
            #getting content
            level = 0
            pos = -1
            for ch in right:
                pos += 1
                if ch == '{':
                    level += 1
                elif ch == '}':
                    level -= 1
                #now check if we are returned to 0 level
                if level == 0:
                    add_space = (pos+1)==len(right) or right[pos+1] not in ["\\", " "]
                    if rm_content:
                        if not rm_slash:
                            result += '\\'
                        if add_space:
                            result += repl + " " + right[pos + 1:]
                        else:
                            result += repl + right[pos + 1:]
                    else:
                        if not rm_slash:
                            result += '\\'
                        if add_space:
                            result+= repl + left_delim+ right[1:pos]+ \
                                    right_delim +" "+ right[pos+1:]
                        else:
                            result+= repl + left_delim+ right[1:pos]+ \
                                    right_delim + right[pos+1:]
                    break
            tex = result
            #next cycle
        else:
            return tex

def replace_command_no_options(tex, command, repl):
    '''This function replace a command without touching
    options and content'''
    r = re.compile(r'(?<=\\)'+command +r'(?![a-zA-Z])')
    return r.sub(repl, tex)


def get_content_greedy(tex, command):
    '''This function get the content of the first occurence of the command
    \command[option]{content}. Option is removed'''
    r = re.search(r'\\' + command +'(\[.*?\])*(?=[\s\{\[])', tex)
    if r:
        right = tex[r.end():].lstrip()
        #getting content
        level = 0
        pos = -1
        for ch in right:
            pos += 1
            if ch == '{':
                level += 1
            elif ch == '}':
                level -= 1
            #now check if we are returned to 0 level
            if level == 0:
                return right[1:pos]


'''Function that returns the content of an environment.
It returns the content matched (start_index, end_index, content).'''
get_environment_content = EnvironmentParser.get_environment_content
'''Function that returns a tuple. Each second member is the content
of the specified environment'''


def environment_split(tex, env):
    #search \begin and end \tag
    pattern = r'\\begin\s*\{\s*'+env+ \
            r'\s*\}(.*?)\\end\s*\{\s*'+env+r'\s*\}'
    content = re.split(pattern, tex, flags=re.DOTALL)
    return content

def command_split(tex, com, remove_options=False):
    '''Function that returns a tuple. The text is split according to
    the occurence of the specified command'''
    pattern = r'\\' + com
    content = re.split(pattern, tex, flags=re.DOTALL)
    return content
