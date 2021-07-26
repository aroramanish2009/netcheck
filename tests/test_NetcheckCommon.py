#!/root/pyats/bin/python
import unittest
'''
Commonly used assert methods

.assertEqual(a, b)      :: a ==b
.assertTrue(x)          :: bool(x) is True
.assertFalse(x)         :: bool(x) is False
.assertIs(a, b)         :: a is b
.assertIsNone(x)        :: x is None
.assertIn(a, b)         :: a in b
.assertIsInstance(a, b) :: isinstance(a, b)

.assertIs(), .assertIsNone(), .assertIn(), and .assertIsInstance() all have 
opposite methods, named .assertIsNot(), and so forth.

Run Command: python -m unittest -v test_NetcheckCommon.py 

'''
import sys
sys.path.insert(0, '../lib/common')
import NetcheckCommon


class TestCommon(unittest.TestCase):
    
    def test_append2list(self):
        '''
        
        Check Method append2list in Class NetcheckCommon.
        Method loops over *argv to append them to a List provided as arg1.

        '''
        test_list = []
        correct_result = [1,2,3]
        check_method = NetcheckCommon.append2list(test_list, 1, 2, 3)
        self.assertEqual(correct_result, check_method)

if __name__ == '__main__':
    unittest.main()
