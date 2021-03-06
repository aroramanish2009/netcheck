'''
layer2check.py

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

from pyats import aetest
from pyats import topology

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

        Mark Class layer2checks to loop for each device in testbed.

        '''
        #Learn model used only supports Cisco products.
        aetest.loop.mark(layer2check,
                         device = [d.name for d in testbed if d.os
                                   in ('ios', 'iosxe','iosxr', 'nxos')])


class layer2check(aetest.Testcase):
    '''layer2check

    < docstring description of this testcase >

    '''

    # testcase groups (uncomment to use)
    # groups = []

    @aetest.setup
    def setup(self, device, testbed):
        for link in testbed.devices[device].links:
            print (link)
        for intf in testbed.devices[device].interfaces:
            if testbed.devices[device].interfaces[intf].mtu:
                print (testbed.devices[device].interfaces[intf].mtu)
        
        device = testbed.devices[device]
        if device.connected:
            self.arp_info = device.learn('arp')
            pprint.pprint(self.arp_info.info)
            self.vlan_info = device.learn('vlan')
            pprint.pprint(self.vlan_info.info)
            self.stp_info = device.learn('stp')
            pprint.pprint(self.stp_info.info)
            self.vxlan_info = device.learn('vxlan')
            pprint.pprint(self.vxlan_info.info)
        pass

    # you may have N tests within each testcase
    # as long as each bears a unique method name
    # this is just an example
    @aetest.test
    def vlan_config_check(self, device, vlans):
        for i in vlans:
            [print (v) for k,v in i.items() if k == device]
        pass

    @aetest.test
    def vlan_status_check(self):
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

