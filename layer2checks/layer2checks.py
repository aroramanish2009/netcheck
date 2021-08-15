'''
layer2checks.py

'''
# see https://pubhub.devnetcloud.com/media/pyats/docs/aetest/index.html
# for documentation on pyATS test scripts

# optional author information
# (update below with your contact information if needed)
__author__ = 'Cisco Systems Inc.'
__copyright__ = 'Copyright (c) 2019, Cisco Systems Inc.'
__contact__ = ['pyats-support-ext@cisco.com']
__credits__ = ['list', 'of', 'credit']
__version__ = 1.0

import logging
import pprint
import sys
import re
sys.path.insert(0, '../lib/common')
import NetcheckCommon

from pyats import aetest
from pyats import topology
from pyats.log.utils import banner

# create a logger for this module
logger = logging.getLogger(__name__)

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def connect(self, testbed):
        '''
        establishes connection to all your testbed devices.
        '''
        # make sure testbed is provided
        assert testbed, 'Testbed is not provided!'

        # connect to all testbed devices
        testbed.connect()
        
    @aetest.subsection
    def prepare_testcases(self, testbed):
        '''
 
        Mark Class checks to loop for each device in testbed.

        '''
        #Learn model used only supports Cisco products.
        aetest.loop.mark(vlan, device = [d.name for d in testbed if d.os
                         in ('ios', 'iosxe', 'nxos')])
        aetest.loop.mark(vxlan, device = [d.name for d in testbed if d.os
                         in ('ios', 'iosxe', 'nxos')])
        aetest.loop.mark(stp, device = [d.name for d in testbed if d.os
                         in ('ios', 'iosxe', 'iosxr')])
        aetest.loop.mark(arp, device = [d.name for d in testbed if d.os
                         in ('ios', 'iosxe', 'nxos', 'iosxr')])



class vlan(aetest.Testcase):
    '''vlan Check

    Tests:
        vlan id & name configured
        vlan interface association
        

    '''

    # testcase groups (uncomment to use)
    # groups = []

    @aetest.setup
    def setup(self, device, testbed):
        device = testbed.devices[device]
        if device.connected:
            self.vlan_info = device.learn('vlan')
            pprint.pprint(self.vlan_info.info)
        else:
            self.failed('Cannot learn %s vlan information: '
                        'did not establish connectivity to device'
                        % device.name)
        vlan_info_out_list = []
        for vlan, data in self.vlan_info.info.items():
            vlans = [k for k, v in data['configuration'].items()]
            for i in vlans:
                if i != '1':
                    vlan_info_out_list.append({x:y for (x,y) in data[i].items() 
                                               if x == 'vlan_id' or x == 'name' or x == 'interfaces' })
        
        if vlan_info_out_list:
            self.vlan_info_out_list = vlan_info_out_list
            aetest.loop.mark(self.vlan_attr_check,
                             vlan_id = (item['vlan_id'] for item in self.vlan_info_out_list))

    # you may have N tests within each testcase
    # as long as each bears a unique method name
    # this is just an example
    @aetest.test
    def vlan_attr_check(self, device, vlans, vlan_id = 'none'):
        try:
            if self.vlan_info_out_list:
                for q in vlans:
                    for k,v in q.items():
                        if k == device:
                            vlan_sot = v
                vlan_sot =  NetcheckCommon.intf_range_expand(vlan_sot)
                print (self.vlan_info_out_list)
                print (vlan_sot)
        except AttributeError:
            self.passed('No Vlans Configured on Device {}'.format(device))

    @aetest.test
    def vlan_inft_check(self):
        pass

    @aetest.cleanup
    def cleanup(self):
        pass
    

class vxlan(aetest.Testcase):
    '''vxlan

    < docstring description of this testcase >

    '''

    # testcase groups (uncomment to use)
    # groups = []

    @aetest.setup
    def setup(self):
        pass

    # you may have N tests within each testcase
    # as long as each bears a unique method name
    # this is just an example
    @aetest.test
    def test(self):
        pass

    @aetest.cleanup
    def cleanup(self):
        pass
    

class stp(aetest.Testcase):
    '''stp

    < docstring description of this testcase >

    '''

    # testcase groups (uncomment to use)
    # groups = []

    @aetest.setup
    def setup(self):
        pass

    # you may have N tests within each testcase
    # as long as each bears a unique method name
    # this is just an example
    @aetest.test
    def test(self):
        pass

    @aetest.cleanup
    def cleanup(self):
        pass
    

class arp(aetest.Testcase):
    '''arp

    < docstring description of this testcase >

    '''

    # testcase groups (uncomment to use)
    # groups = []

    @aetest.setup
    def setup(self):
        pass

    # you may have N tests within each testcase
    # as long as each bears a unique method name
    # this is just an example
    @aetest.test
    def test(self):
        pass

    @aetest.cleanup
    def cleanup(self):
        pass
    


class CommonCleanup(aetest.CommonCleanup):
    '''CommonCleanup Section

    < common cleanup docstring >

    '''

    # uncomment to add new subsections
    # @aetest.subsection
    # def subsection_cleanup_one(self):
    #     pass

if __name__ == '__main__':
    # for stand-alone execution
    import argparse
    from pyats import topology

    parser = argparse.ArgumentParser(description = "standalone parser")
    parser.add_argument('--testbed', dest = 'testbed',
                        help = 'testbed YAML file',
                        type = topology.loader.load,
                        default = None)

    # do the parsing
    args = parser.parse_known_args()[0]

    aetest.main(testbed = args.testbed)
