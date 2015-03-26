from types import FunctionType 
from copy import copy 


class OptionsDictException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

        
class OptionsDict(dict):
    """
    OptionsDict(name, entries={})
    
    An OptionsDict inherits from a conventional dict, but it has a few
    enhancements:

    (1) Values can be runtime-dependent upon the state of other values
    in the dict.  Each of these special values is specified by a
    function accepting a single dictionary argument (i.e. the
    OptionsDict itself).  The dictionary argument is used to look
    things up dynamically.

    (2) An OptionsDict has a name which distinguishes it from possible
    siblings in an iterable sequence.

    (3) A combination of OptionsDicts can be added together, in which
    case the names are concatenated to form a unique ID and the
    entries merged.
    
    """
    def __init__(self, name, entries={}):
        if isinstance(name, str):
            self.name = name
        else:
            raise OptionsDictException(
                "name argument must be a string.")
        # the dict superclass will check that the entries argument is
        # acceptable
        dict.__init__(self, entries)

    def __repr__(self):
        return self.name
            
    def __getitem__(self, key):
        value = dict.__getitem__(self, key)
        # recurse until the return value is no longer a function
        if isinstance(value, FunctionType):
            return value(self)
        else:
            return value
            
            
class CallableEntry:
    """
    CallableEntry(function)

    Because the OptionsDict works by evaluating all function objects
    recursively, it is not able to return other functions specified by
    the client unless these are wrapped as callable objects.  This
    class provides such a wrapper.
    """
    def __init__(self, function):
        self.function = function
        
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    
        
def create_sequence(sequence_key, elements):
    """
    create_sequence(sequence_key, elements)

    Creates a list of OptionsDicts, converting the given elements if
    necessary.  That is, if a element is not already an OptionsDict, it
    is converted to a string which becomes the name of a new
    OptionsDict.

    An important feature is that for each element, the corresponding
    OptionsDict acquires the entry {sequence_key: element.name} if the
    element is already OptionsDict, and {sequence_key: element}
    otherwise.
    """
    options_dict_list = []
    for el in elements:
        if isinstance(el, OptionsDict):
            # If the element is already an OptionsDict object, make a
            # copy.  This has the benefit of preventing side effects
            # if the element persists elsewhere.
            od = copy(el)
            # add a special entry using sequence_key
            od.update({sequence_key: str(el)})
        else:
            # instantiate a new OptionsDict with the string
            # represention of the element acting as its name, and the
            # original element stored under sequence_key
            od = OptionsDict(str(el), {sequence_key: el})
        options_dict_list.append(od)
    return options_dict_list

