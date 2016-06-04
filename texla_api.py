import log
from flask import Flask, request, jsonify
import json
import os, random, string
from texla.Parser import Parser
from texla.Renderers.MediaWikiRenderer import MediaWikiRenderer

app = Flask('texla_api')
app.secret_key = 'abcdef'

@app.route('/')
def welcome():
    return "Welcome to TeXLa!"

@app.route('/texla')
def helloworld():
    return "Start to import :)"

if __name__ == '__main__':
        app.run(host="127.0.0.1", port=5000, debug=True)
