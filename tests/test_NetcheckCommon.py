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

    def test_intf_range_expand(self):
        '''

        Check Method intf_range_expand in Class NetcheckCommon.
        Method loops over list_of_dict, check for key 'Interfaces' and 
        replaces range of interfaces to individual interfaces.
        Ex: [{'30': {'name': 'test', 'interfaces': ['Port-channel2', 'Ethernet1/5-6']}}]
        To
        [{'30': { 'name': 'test', 'interfaces': ['Port-channel2', 'Ethernet1/5', 'Ethernet1/6']}}]

        '''
        mylist = [{'30': {'name': 'test', 'interfaces': ['Port-channel2', 'Ethernet1/5-6']}}, {'40': {'name': 'test2'}}]
        expaned_mylist = [{'30': { 'name': 'test', 'interfaces': ['Port-channel2', 'Ethernet1/5', 'Ethernet1/6']}}, {'40': {'name': 'test2'}}]
        check_method = NetcheckCommon.intf_range_expand(mylist)
        self.assertEqual(expaned_mylist, check_method)

    def test_dict_filter(self):
        '''
        Check Method dict_filter in Class NetcheckCommon.
        Method itreates over dict and only keeps key/value
        whose keys are present in the set. Returns dict with 
        input as dict & set. 
        '''
        mydict = {'interfaces': ['Port-channel21', 'Ethernet1/6'], 'mode': 'ce', 'name': 'test', 'shutdown': False, 'type': 'enet', 'vlan_id': '30'}
        myset = ('interfaces', 'name','vlan_id')
        new_mydict =  {'interfaces': ['Port-channel21', 'Ethernet1/6'], 'name': 'test', 'vlan_id': '30'}
        check_method = NetcheckCommon.dict_filter(mydict, myset)
        self.assertEqual(new_mydict,check_method)

if __name__ == '__main__':
    unittest.main()
