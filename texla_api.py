from flask import Flask, request, jsonify
import json
import os, random, string
from texla.Parser import Parser
from texla.Renderers.MediaWikiRenderer import MediaWikiRenderer


app = Flask('texla_api')
app.secret_key = 'abcdef'

@app.route('/texla')
def helloworld():
    return "hello world!"


if __name__ == '__main__':
        app.run(host="0.0.0.0", port=5000, debug=True)
