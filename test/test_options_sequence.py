import sys
sys.path.append('..')

import unittest
from options import OptionsDict, OptionsDictException
from re import sub

        
class TestOptionsDictSequence(unittest.TestCase):

    def setUp(self):
        """
        I create an OptionsDict sequence from a list of
        different-typed values, one of which is already an
        OptionsDict.
        """
        od = OptionsDict.named('some_dict', {'foo': 'bar'})
        self.values = ['A', od, 2, 3.14]
        self.seq = OptionsDict.sequence('random_thing', self.values)
        
    def test_element_types(self):
        """
        Each element in the sequence should be an OptionsDict.
        """
        for el in self.seq:
            self.assertIsInstance(el, OptionsDict)

    def test_element_names(self):
        """
        The name of each element, given by its string representation,
        should be identical to the string representation of the
        corresponding initial value.
        """
        for el, v in zip(self.seq, self.values):
            self.assertEqual(str(el), str(v))

    def test_element_dicts(self):
        """
        While all the elements should be dictionaries, only the
        preexisting OptionsDict should have the {'foo': 'bar'} entry.
        """
        for i, el in enumerate(self.seq):
            lookup = lambda: el['foo']
            if i==1:
                self.assertEqual(lookup(), 'bar')
            else:
                self.assertRaises(KeyError, lookup)

    def test_lookup_sequence_key(self):
        """
        When the sequence key is looked up in each element, the
        element should return the corresponding initial value.  The
        initial value representation of the preexisting OptionsDict is
        simply its name.
        """
        for i, el in enumerate(self.seq):
            result = el['random_thing']
            if i==1:
                self.assertEqual(result, 'some_dict')
            elif i==3:
                # careful with floats
                self.assertAlmostEqual(result, 3.14)
            else:
                self.assertEqual(result, self.values[i])
        

class TestOptionsDictSequenceCreationOptions(unittest.TestCase):

    def test_create_with_common_entries(self):
        """
        I create an OptionsDict sequence 'A' using three integers and
        common entry {'foo': 'bar'}.  All elements should have this
        entry.
        """
        seq = OptionsDict.sequence('A', range(3), {'foo': 'bar'})
        for el in seq:
            self.assertEqual(el['foo'], 'bar')

    def test_create_with_bad_common_entries(self):
        """
        I create an OptionsDict sequence 'A' using three integers and
        something that is not a dictionary for the common_entries
        argument.  An error should be raised.
        """
        create_seq = lambda: \
            OptionsDict.sequence('A', range(3), 'foo')
        self.assertRaises(OptionsDictException, create_seq)

    def test_format_names_with_string(self):
        """
        I create an OptionsDict sequence 'A' using integers 2, 5, 10.
        Format the element names as A02, A05, A10.
        """
        seq = OptionsDict.sequence('A', [2, 5, 10],
                                   name_format='A{:02g}')
        expected_names = ['A02', 'A05', 'A10']
        for el, expected in zip(seq, expected_names):
            self.assertEqual(str(el), expected)

    def test_format_names_with_function(self):
        """
        I create an OptionsDict sequence 'A' using floats 1, 2.5,
        6.25.  Format the element names as 1p00, 2p50, 6p25.
        """
        formatter = lambda x: '{:.2f}'.format(x).replace('.', 'p')
        seq = OptionsDict.sequence('A', [1., 2.5, 6.25],
                              name_format=formatter)
        expected_names = ['1p00', '2p50', '6p25']
        for el, expected in zip(seq, expected_names):
            self.assertEqual(str(el), expected)

    def test_format_names_with_bad_formatter(self):
        """
        I create an OptionsDict sequence with an inappropriate object
        as name_format.  An error should be raised.
        """
        create_seq = lambda: \
            OptionsDict.sequence('A', [1., 2.5, 6.25],
                                 name_format=None)
        self.assertRaises(OptionsDictException, create_seq)

        
if __name__ == '__main__':
    unittest.main()
        
