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
        aetest.loop.mark(stp, device = [d.name for d in testbed if d.os
                         in ('ios', 'iosxe', 'nxos')])
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
        global dev_os
        dev_os = [d.os for d in testbed if d.name in device][0]
        device = testbed.devices[device]
        
        if device.connected and dev_os != 'iosxr':
            self.vlan_info_in = device.parse('show vlan')
            #pprint.pprint(self.vlan_info_in)
        else:
            self.failed('Cannot learn %s vlan information: '
                        'did not establish connectivity to device'
                        % device.name)
        if self.vlan_info_in:
            default_vlans = ['1','1002','1003','1004','1005']
            mykeys = ('interfaces','name')
            for kv,vv in self.vlan_info_in.items():
                for default_vlan in default_vlans:
                    vv.pop(default_vlan, None)
            for kvv,vvv in vv.items():
                vvv = NetcheckCommon.dict_filter(vvv,mykeys)
                vv[kvv] = vvv
            if vv:
                self.vlan_info_out = [vv]


    # you may have N tests within each testcase
    # as long as each bears a unique method name
    # this is just an example
    @aetest.test
    def vlan_config_check(self, device, vlans):
        try:
            if self.vlan_info_out:
                vlan_sot = []
                for q in vlans:
                    for k,v in q.items():
                        if k == device:
                            vlan_sot = NetcheckCommon.intf_range_expand(v)
                if vlan_sot:
                    vlansindeviceconfig = [ k for k,v in self.vlan_info_out[0].items()]
                    vlansinsot = [ k for k,v in vlan_sot[0].items()]
                    vlansmissingindeviceconfig = [item for item in vlansinsot if item not in vlansindeviceconfig ]
                    vlansmissinginsot = [ item for item in vlansindeviceconfig if item not in vlansinsot ]
                    if vlansmissinginsot and not vlansmissingindeviceconfig:
                        self.failed('List of Vlans configured on device but missing in SOT: {}'.format(vlansmissinginsot)) 
                    elif vlansmissingindeviceconfig and not vlansmissinginsot:
                        self.failed('List of Vlans present in SOT but not configured on Device: {}'.format(vlansmissingindeviceconfig))
                    elif vlansmissingindeviceconfig and vlansmissinginsot:
                        self.failed('List of Vlans present in SOT but not configured on Device: {} and List of Vlans configured on device but missing in SOT: {}'.format(vlansmissingindeviceconfig,vlansmissinginsot))
                    else:
                        self.passed('No Vlans Mismatch on Device {}.'.format(device))
        except AttributeError:
            self.skipped('No Vlans Configured on Device {}.'.format(device))
        
    @aetest.test
    def vlan_association_check(self, device, vlans):
        try:
            if self.vlan_info_out:
                vlan_sot = []
                for q in vlans:
                    for k,v in q.items():
                        if k == device:
                            vlan_sot = NetcheckCommon.intf_range_expand(v)

                if vlan_sot: 
                    diffrential = []
                    for item in vlan_sot:
                        for k,v in item.items():
                            for item1 in self.vlan_info_out:
                                for k1,v1 in item1.items():
                                    if k == k1 and v != v1:
                                        mydict = {'vlan': k, 'SOT': v, 'CONFIGURED': v1}
                                        diffrential.append(mydict)
                    if diffrential:
                        self.failed('Mismatch Detected between SOT & Configured: {}'.format(diffrential))
                else:
                    self.skipped('No Vlans Data found in SOT for Device: {}.'.format(device))

            self.passed('VLAN-ID configuration in Source of Truth matches device configuration and vice versa.')
        except AttributeError:
            self.skipped('No Vlans Configured on Device {}.'.format(device))

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
    def setup(self, device, testbed):
        global dev_os
        dev_os = [d.os for d in testbed if d.name in device][0]
        device = testbed.devices[device]

        if device.connected and dev_os != 'iosxr':
            self.stp_info = device.parse('show spanning-tree detail')
            pprint.pprint(self.stp_info)
        else:
            self.failed('Cannot learn %s STP information: '
                        'did not establish connectivity to device'
                        % device.name)


    # you may have N tests within each testcase
    # as long as each bears a unique method name
    # this is just an example
    @aetest.test
    def stp_mode_check(self, device, stpinfo):
        try:
            if self.stp_info:
                for item in stpinfo:
                    for k,v in item.items():
                        if k == device:
                            stp_mode = v.get('stp_mode')
                for k,v in self.stp_info.items():
                    if k == stp_mode:
                        self.passed('Configured STP Mode: {} Matches SOT STP Mode: {}.'.format(k,stp_mode))
                    else:
                        self.failed('Configured STP Mode: {} Does Not Match SOT STP Mode: {}.'.format(k,stp_mode))
        except AttributeError:
            self.skipped('No Spanning Tree Information discovered on Device {}.'.format(device))

    @aetest.test
    def stp_bridge_priority(self, device, stpinfo):
        try:
           if self.stp_info:
               for item in stpinfo:
                   for k,v in item.items():
                       if k == device:
                           sot_bridge_priority = v.get('stp_priority')
               if sot_bridge_priority:
                   for k,v in self.stp_info.items():
                       for kv,vv in v.items():
                           if kv == 'vlans':
                               for kvv,vvv in vv.items():
                                   vlan_bp = vvv.get('bridge_priority')
                                   if vlan_bp and vlan_bp != sot_bridge_priority:
                                       self.failed('Configured Bridge Priority {} Does Not Match SOT Bridge Priority for Vlan {} in Device {}'.format(vlan_bp,kvv,device))
                   self.passed('No Mismatch identified for for Device {}'.format(device)) 
               else:
                   self.skipped('No Bridge Priority discovered in SOT for device {}'.format(device))
        except AttributeError:
            self.skipped('No Spanning Tree Information discovered on Device {}.'.format(device))

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
    def setup(self, device, testbed):
        device = testbed.devices[device]
        if device.connected:
            self.arp_info = device.learn('arp')
            pprint.pprint(self.arp_info.info)
        else:
            self.failed('Cannot learn %s ARP information: '
                        'did not establish connectivity to device'
                        % device.name)
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
