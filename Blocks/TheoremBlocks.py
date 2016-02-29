import logging
import re
from . import utility
from . import CommandParser
from .Block import *

class Theorem():

    def __init__(self, name, definition,star,
                 counter,numberby):
        self.name = name
        self.definition = definition
        self.star = star
        self.counter = counter
        self.numberby = numberby
