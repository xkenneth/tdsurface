import re
from las.file import *
from las.headers import *
from util import subdivide
import test.data as data

start_symbols = ["~A", "~C", "~W", "~P", "~V"]
white_space = ["\n", "\r", "\t", " "]
num_regex = "-?\d+([.]\d+)?"
num_chars = "-1234567890."

def is_number(text):
    match = re.match(num_regex, text)
    if match:
        start = match.start()
        end = match.end()
        return (end - start) == len(text)
    else:
        return False

def to_num(text):
    if "." in text:
        return float(text)
    else:
        return int(text)

def to_chars(string):
    result = ""
    for c in string:
        if c == "\n":
            result = result + "\\n"
        elif c == "\r":
            result = result + "\\r"
        else:
            result = result + c
    return result

class BaseParser:
    def __init__(self, input):
        self.input = input
        self.cursor = 0
        self.length = len(self.input)
        self.limit = self.length
        self.excursions = []

    def GuardLimit(method):
        def f(obj, *args, **kwargs):
            if not obj.at_limit():
                return method(obj,*args, **kwargs)
        return f

    def restart(self):
        self.cursor = 0
        self.limit = self.length

    def limit_line(self,f):
        old_limit = self.limit
        self.limit = self.index_of("\n")
        ret = f()
        self.limit = old_limit
        return ret
        
    def index_of(self, target):
        self.push_excursion()
        found = False
        while not self.at_limit() and not found:
            if self.match_inc(target):
                found = True
            else:
                self.cursor += 1
        cursor = self.cursor
        self.pop_excursion()
        return cursor
        
    def push_excursion(self):
        self.excursions.append([self.cursor, self.limit])

    def pop_excursion(self):
        self.cursor,self.limit = self.excursions.pop()
        
    def save_excursion(self, fn):
        self.push_excursion()
        ret = fn()
        self.pop_excursion()
        return ret

    def at_limit(self):
        return self.cursor >= self.limit

    def zapto_last(self, target):
        start = self.cursor
        last_index = self.cursor
        while not self.at_limit():
            if self.match_inc(target):
                last_index = self.cursor
            self.cursor += 1
        self.cursor = last_index
        return self.input[start:self.cursor]
        
    def zapto(self,target):
        start = self.cursor
        found = False
        while not self.at_limit() and not found:
            if self.match_inc(target):
                found = True
            else:
                self.cursor += 1
        return self.input[start:self.cursor]

    def upto(self,target):
        result = self.zapto(target)
        if not self.at_limit():
            result = result[:-1]
        return result

    def upto_last(self, target):
        result = self.zapto_last(target)[:-1]
        if not self.at_limit():
            result = result[:-1]
        return result

    def skip(self,target):
        found = False
        while not self.at_limit() and not found:
            if self.match_inc(target):
                found = True
            else:
                self.cursor += 1
        
    def match(self, target):
        tlen = len(target)
        return self.input[self.cursor:self.cursor+tlen] == target

    def match_inc(self, target):
        matches = self.match(target)
        if matches: self.cursor += len(target)
        return matches

    def drop_line(self):
        self.upto("\n")

    def skip_spaces(self):
        done = False
        while self.cursor < self.length and not done:
            c = self.input[self.cursor]
            if c in white_space:
                self.cursor += 1
            elif c == "#":
                self.drop_line()
            else:
                done = True

    def goto_line(self, target):
        def match_skip_space():
            self.skip_spaces()
            return self.match(target)

        found = False
        while not self.at_limit() and not found:
            if match_skip_space():
                found = True
            else:
                self.drop_line()

    def zap_line(self):
        return self.upto("\n")
    
    def char(self):
        return self.input[self.cursor]
            
            
class Parser(BaseParser):

    def __init__(self, input):
        BaseParser.__init__(self, input)

    def las_file(self):
        version_header = self.save_excursion(self.version_header)
        well_header = self.save_excursion(self.well_header)
        curve_header = self.save_excursion(self.curve_header)
        parameter_header = self.save_excursion(self.parameter_header)
        las_data = self.save_excursion(lambda: self.las_data(curve_header))
        return LasFile(version_header,
                       well_header,
                       curve_header,
                       parameter_header,
                       las_data)
        
    def well_header(self): 
        self.goto_line("~W")
        self.drop_line()
        descriptors = self.descriptors()
        return WellHeader(descriptors)
        
    def version_header(self):
        self.goto_line("~V")
        self.drop_line()
        self.skip("VERS.")
        version = self.upto(":").strip()
        version = to_num(version)        

        self.skip("WRAP.")
        wrap = self.upto(":").strip()
        if wrap == "NO": 
            wrap = False
        elif wrap == "YES":
            wrap = True
        else:
            raise "WRAP NOT RECOGNIZED"

        return VersionHeader(version, wrap)

    def curve_header(self):
        self.goto_line("~C")
        self.drop_line()
        descriptors = self.descriptors()
        return CurveHeader(descriptors)

    def parameter_header(self):
        self.goto_line("~P")
        self.drop_line()
        descriptors = self.descriptors()
        return ParameterHeader(descriptors)

    def las_data(self, curve_header):
        self.goto_line("~A")
        self.drop_line()
        data = self.get_numbers()
        curves = LasCurve.from_rows(subdivide(data, len(curve_header.descriptors)),
                                    curve_header)
        return curves

    #micro-optimized
    def get_numbers(self):
        nums = []
        while self.cursor < self.length:
            #get_number begin
            start = self.cursor
            while self.cursor < self.length and self.input[self.cursor] in num_chars:
                self.cursor += 1
            num = self.input[start:self.cursor]
            #get_number end

            if num != '':
                if "." in num:
                    nums.append(float(num))
                else:
                    nums.append(int(num))
            #begin skip_spaces
            done = False
            while not done and self.cursor < self.length:
                c = self.input[self.cursor]
                if c in white_space:
                    self.cursor += 1
                elif c == '#':
                    self.drop_line()
                else:
                    done = True
            #end skip_spaces
        return nums

    def descriptors(self):
        descriptor = self.descriptor()
        acc = []
        while descriptor: 
            acc.append(descriptor)
            descriptor = self.descriptor()
        return acc

    def descriptor(self):
        self.skip_spaces()
        if self.at_limit(): return None
        if self.input[self.cursor:self.cursor+2] in start_symbols: return
        def preprocess(stuff):
            stuff = stuff.strip()
            if stuff == "":
                return None
            elif is_number(stuff):
                return to_num(stuff)
            else:
                return stuff
        mnemonic = preprocess(self.upto("."))
        unit = preprocess(self.upto(" "))
        data = preprocess(self.limit_line(lambda: self.upto_last(":")))
        description = preprocess(self.zap_line())
        return Descriptor(mnemonic, unit, data, description)

    def backtrack(self, text):
        self.cursor -= len(text)
