from types import FunctionType
from copy import copy
from string import Template


# default settings
name_separator = '_'
template_expansion_max_loops = 5


class OptionsDictException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

        
class OptionsDict(dict):
    """
    OptionsDict(name, entries={})
    OptionsDict.anonymous(entries={})
    
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

    name = ''
    name_separator = name_separator
    template_expansion_max_loops = template_expansion_max_loops
    
    def __init__(self, name, entries={}):
        # check argument types
        if not name:
            name = ''
        elif not isinstance(name, str):
                raise OptionsDictException(
                    "name argument must be a string (or None).")
        if not isinstance(entries, dict):
            raise OptionsDictException(
                    "entries argument must be a dictionary.")
        # store name, initialise superclass
        self.name = name
        dict.__init__(self, entries)
            

    def __repr__(self):
        return self.name + ':' + dict.__repr__(self)

    def __str__(self):
        return self.name

    def __iter__(self):
        yield self
    
    def __getitem__(self, key):
        value = dict.__getitem__(self, key)
        # recurse until the return value is no longer a function
        if isinstance(value, FunctionType):
            # dynamic entry
            return value(self)
        else:
            # normal entry
            return value
        
    def __eq__(self, other):
        eq_names = str(self)==str(other)
        eq_dicts = dict.__eq__(self, other)
        return eq_names and eq_dicts

    def __ne__(self, other):
        return not self==other

    def __add__(self, other):
        names = (str(self), str(other))
        if all(names):
            new_name = name_separator.join(names)
        else:
            new_name = ''.join(names)
        result = OptionsDict(new_name, self)
        result.update(other)
        return result

    def __radd__(self, other):
        if not other:
            return self
        else:
            return self + other

    def expand_template(self, buffer_string, 
                        max_loops=template_expansion_max_loops):
        """In buffer_string, replaces all substrings prefixed '$' with
        corresponding values from the dictionary."""
        n = 0
        while '$' in buffer_string and n < max_loops:
            buffer_string = Template(buffer_string)
            buffer_string = buffer_string.safe_substitute(self)
            n += 1
        return buffer_string



        
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

    
def create_sequence(sequence_key, elements, common_entries={}, 
                    name_format='{}'):
    """
    create_sequence(sequence_key, elements, common_entries={},
                    name_format='{}',)

    Creates a list of OptionsDicts, converting the given elements if
    necessary.  That is, if a element is not already an OptionsDict,
    it is converted to a string which becomes the name of a new
    OptionsDict.  All dicts are initialised with common_entries if
    this argument is given.

    The string conversion is governed by name_format, which can either
    be a format string or a callable that takes the element value and
    returns a string.

    An important feature is that for each element, the corresponding
    OptionsDict acquires the entry {sequence_key: element.name} if the
    element is already OptionsDict, and {sequence_key: element}
    otherwise.
    """
    optionsdict_list = []
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
            try:
                od = OptionsDict(name_format(el),
                                 {sequence_key: el})
            except TypeError:
                try:
                    od = OptionsDict(name_format.format(el),
                                     {sequence_key: el})
                except AttributeError:
                    raise OptionsDictException(
                        "name_formatter must be a callable or a format string.")
        # check and add common_entries
        if not isinstance(common_entries, dict):
            raise OptionsDictException(
                    "common_entries argument must be a dictionary.")
        od.update(common_entries)
        # append to the list
        optionsdict_list.append(od)
    return optionsdict_list

