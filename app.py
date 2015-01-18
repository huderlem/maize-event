# by Marcus Huderle, 2015

import os
from flask import flask

app = Flask(__name__)

@app.route('/')
def index():
	return 'Hello Worldp'

