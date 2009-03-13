import re
from file import HasDescriptors
from util import lfind

class VersionHeader(object):
    def __init__(self, version, wrap): 
        self.version = version
        self.wrap = wrap

    def wrap_string(self):
        if self.wrap: return "YES"
        else: return "NO"
            
    def __str__(self):
        return "version = %s, wrap = %s" % (self.version, self.wrap)

    def __repr__(self):
        return self.__str__()

    def __eq__(self,that):
        return (isinstance(that, VersionHeader) and
                self.version == that.version and
                self.wrap == that.wrap)

    def to_las(self):
        return ("~Version information\n" +
                "VERS. %s:\n" % self.version + 
                "WRAP. %s:\n" % self.wrap_string())
        

class HeaderWithDescriptors(HasDescriptors):
    def __str__(self):
        return "%s(descriptors = %s)" % (self.__class__.__name__, self.descriptors)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, that):
        if not isinstance(that, self.__class__): return False
        return (self.descriptors == that.descriptors)

    def __getattr__(self, attr):
        if attr in self.__dict__: 
            return self.__dict__[attr]
        else:
            descriptor = lfind(self.descriptors, 
                               lambda d: d.mnemonic.lower() == attr)
            if not descriptor:
                print "attr %s not found in %s " % (attr, self.mnemonics())
                raise AttributeError
            return descriptor

    def to_las(self):
        return (self.identifier + "\n" + 
                "\n".join([d.to_las() for d in self.descriptors]) + "\n")


def descriptor_header(name, identifier):
    class Anon(HeaderWithDescriptors):
        def __init__(self, descriptors):
            self.identifier = identifier
            self.descriptors = descriptors
    Anon.__name__ = name
    return Anon

CurveHeader = descriptor_header("CurveHeader","~Curve")
WellHeader = descriptor_header("WellHeader","~Well")
ParameterHeader = descriptor_header("ParameterHeader","~Parameter")
