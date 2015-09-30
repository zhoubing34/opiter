import unittest
from options_dict import OptionsDict, CallableEntry, OptionsDictException
from options_node import OptionsNode
from options_array import OptionsArray
from formatters import SimpleFormatter, TreeFormatter
from copy import deepcopy

class TestOptionsDictBasics(unittest.TestCase):

    def setUp(self):
        self.od = OptionsDict({})
        
    def test_str(self):
        """
        Because there is no node information, str() should return an empty
        string.
        """
        self.assertEqual(str(self.od), '')
    
    def test_create_node_info_formatter_default(self):
        self.assertIsInstance(
            self.od.create_node_info_formatter(), SimpleFormatter)
    
    def test_create_node_info_formatter_simple(self):
        self.assertIsInstance(
            self.od.create_node_info_formatter('simple'), SimpleFormatter)

    def test_create_node_info_formatter_tree(self):
        self.assertIsInstance(
            self.od.create_node_info_formatter('tree'), TreeFormatter)

    def test_create_node_info_formatter_error(self):
        self.assertRaises(
            OptionsDictException, 
            lambda: self.od.create_node_info_formatter('madethisup'))
        


class TestOptionsDictInteractionsWithNode(unittest.TestCase):

    def setUp(self):
        self.node = OptionsNode('foo')
        self.od = OptionsDict(entries={'bar': 1})

    def test_donate_copy(self):
        """
        Passing a node to OptionsDict's donate_copy method should furnish
        the node with dictionary information.
        """
        od_init = deepcopy(self)
        self.node, remainder = self.od.donate_copy(self.node)
        node_od = self.node.collapse()[0]
        self.assertEqual(node_od['bar'], 1)
        self.assertEqual(len(remainder), 0)


class TestOptionsDictAfterTreeCollapse(unittest.TestCase):

    def setUp(self):
        """
        Run tests on this tree:
        0: a
            1: a
                2: a
                2: b
                2: c
            1: b
                2: a
                2: b
                2: c
        """
        self.tree = OptionsArray('0', ['a']) * \
                    OptionsArray('1', ['a', 'b']) * \
                    OptionsArray('2', ['a', 'b', 'c'])
        
    def test_str_tree(self):
        ods = self.tree.collapse()
        expected = """
0: a
    1: a
        2: a
        2: b
        2: c
    1: b
        2: a
        2: b
        2: c"""
        result = ''.join(['\n' + od.get_string(formatter='tree') \
                          for od in ods])
        self.assertEqual(result, expected)

        
    def test_indent(self):
        ods = self.tree.collapse()
        expected = ('\n' + ' '*12)*6
        result = ''.join(['\n' + od.indent() for od in ods])
        self.assertEqual(result, expected)

        
        
class TestCallableEntry(unittest.TestCase):

    def setUp(self):
        """
        I create an OptionsDict with a callable entry stored under
        'my_func'.  
        """
        self.od = OptionsDict({
            'my_func': CallableEntry(lambda a, b=1: a + b)})

    def test_as_function(self):
        """
        The callable should not evaluate like a dynamic entry but instead
        remain intact and work as intended.
        """
        self.assertIsInstance(self.od['my_func'], CallableEntry)
        self.assertEqual(self.od['my_func'](1), 2)
        self.assertEqual(self.od['my_func'](1, 2), 3)

    def test_freeze(self):
        """
        Freezing should not affect the existence of the callable.
        """
        self.od.freeze()
        self.od['my_func']

    def test_freeze_and_clean(self):
        """
        Freezing with the clean option should remove the callable so that
        the whole object is safe to pickle.
        """
        self.od.freeze(clean=True)
        self.assertRaises(KeyError, lambda: self.od['my_func'])

        
if __name__ == '__main__':
    unittest.main()
