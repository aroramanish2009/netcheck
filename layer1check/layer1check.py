'''
layer1check.py

'''
# see https://pubhub.devnetcloud.com/media/pyats/docs/aetest/index.html
# for documentation on pyATS test scripts

__author__ = 'The Last Packet Bender'
__copyright__ = 'Do not use it..anywhere'
__contact__ = ['#aroramanish2009']
__credits__ = ['list', 'of', 'credit']
__version__ = 0.1

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
        Establishes connection to all your testbed devices.
        '''
        # make sure testbed is provided
        assert testbed, 'Testbed is not provided!'

        # connect to all testbed devices
        testbed.connect()
        
    @aetest.subsection
    def prepare_testcases(self, testbed):
        '''
    
        Mark Class layer1checks to loop for each device in testbed.
      
        '''
        #Learn model used only supports Cisco products.
        aetest.loop.mark(layer1checks,
                         device = [d.name for d in testbed if d.os
                                   in ('ios', 'iosxe', 'iosxr', 'nxos')])


class layer1checks(aetest.Testcase):
    '''Common layer1 checks

    Check counter for CRC, Input/Output Errors, Discards,
    Duplex, Individual & Port-Channel Member port UP/Down status. 

    '''

    # testcase groups (uncomment to use)
    # groups = []

    @aetest.setup
    def setup(self, device, testbed):
        '''
        
        Learn layer1 model for devices in the loop. 
        
        '''
        device = testbed.devices[device]
       
        logger.info(banner("Gathering Interface Information from %s"
                           % device))

        if device.connected:
            #Refer to Genie Libs for learn model reference
            self.interface_info = device.learn('interface')
            #pprint.pprint(self.interface_info.info)
        else:
            self.failed('Cannot learn %s interface information: '
                        'did not establish connectivity to device'
                        % device.name)
        #Create simple datasets for test cases.
        crc_info_out_list = []
        discard_info_out_list = []
        error_info_out_list = []
        dupl_info_out_list = []
        inft_status_out_list = []
        inft6_status_out_list = []
        mtu_info_out_list = []
        lag_no_mem_out_list = []
        lag_mem_down_out_list = []
        for intf, data in self.interface_info.info.items():
            counters = data.get('counters')
            descript = data.get('description')
            if counters:
                #CRC Counter Check
                crc_info_in_list = []
                crc_info_in_list = NetcheckCommon.append2list(crc_info_in_list, 
                                                              device, intf, descript)
                if 'in_crc_errors' in counters and counters['in_crc_errors'] != 0 :
                    crc_info_in_list.append(counters['last_clear'])
                    crc_info_in_list.append(str(counters['in_crc_errors']))
                    crc_info_out_list.append(crc_info_in_list)
                #Discards Counter Check
                discard_info_in_list = []
                discard_info_in_list = NetcheckCommon.append2list(discard_info_in_list,
                                                                  device, intf, descript)
                if 'out_discard' in counters and counters['out_discard'] != 0:
                    discard_info_in_list.append(str(counters['out_discard']))
                    discard_info_in_list.append('out_discard')
                    discard_info_out_list.append(discard_info_in_list)
                elif 'in_discards' in counters and counters['in_discards'] != 0 :
                    discard_info_in_list.append(str(counters['in_discards']))
                    discard_info_in_list.append('in_discards')
                    discard_info_out_list.append(discard_info_in_list)
                #Error Counters Check
                error_info_in_list = []
                error_info_in_list = NetcheckCommon.append2list(error_info_in_list,
                                                                device, intf, descript)
                if 'in_errors' in counters or 'out_errors' in counters:
                    try:
                        if counters['in_errors'] != 0 or counters['out_errors'] != 0:
                            error_info_in_list.append(str(counters['in_errors']))
                            error_info_in_list.append('in_errors')
                            error_info_in_list.append(str(counters['out_errors']))
                            error_info_in_list.append('out_errors')
                            error_info_out_list.append(error_info_in_list)
                    except:
                        if counters['out_errors'] != 0:
                            error_info_in_list.append(str(counters['out_errors']))
                            error_info_in_list.append('out_errors')
                            error_info_out_list.append(error_info_in_list)
            #Duplex Field Check
            duplex_mode = data.get('duplex_mode')
            osta = data.get('oper_status')
            dupl_info_in_list = []
            dupl_info_in_list = NetcheckCommon.append2list(dupl_info_in_list,
                                                           device, intf, descript)
            if duplex_mode and duplex_mode == 'half':
                dupl_info_in_list.append(duplex_mode)
                dupl_info_out_list.append(dupl_info_in_list)  
            #MTU Verification with topology in testbed
            mtu_info = data.get('mtu')
            mtu_info_in_list = []
            mtu_info_in_list = NetcheckCommon.append2list(mtu_info_in_list,
                                                          device, intf, descript)
            if mtu_info:
                for topo_inft in device.interfaces:
                    if topo_inft == intf and device.interfaces[topo_inft].mtu:
                        if device.interfaces[topo_inft].mtu != mtu_info:
                            mtu_info_in_list.append(device.interfaces[topo_inft].mtu)
                            mtu_info_in_list.append(mtu_info)
                            mtu_info_out_list.append(mtu_info_in_list)
                 
            #LAG Checks
            pc_mode = data.get('port_channel')
            if pc_mode:
                lag_no_mem_in_list = []
                lag_no_mem_in_list = NetcheckCommon.append2list(lag_no_mem_in_list,
                                                                device, intf, descript)
                if pc_mode['port_channel_member'] == False and re.search("Port-channel", intf):
                    lag_no_mem_in_list.append(pc_mode['port_channel_member'])
                    lag_no_mem_out_list.append(lag_no_mem_in_list)
                elif pc_mode['port_channel_member'] == True and osta != 'up' and not re.search("Port-channel", intf):
                    lag_no_mem_in_list.append(pc_mode['port_channel_int'])
                    lag_no_mem_in_list.append(osta)
                    lag_mem_down_out_list.append(lag_no_mem_in_list)
              
            #IPv4 and IPv6 Interface Operational Status
            ipv4 = data.get('ipv4')
            ipv6 = data.get('ipv6')
            if ipv4 and osta != 'up':
                inft_status_in_list = []
                inft_status_in_list = NetcheckCommon.append2list(inft_status_in_list,
                                                                 device, intf, descript)
                for cidr, value in ipv4.items():
                    inft_status_in_list.append(cidr)
                inft_status_out_list.append(inft_status_in_list)
            if ipv6 and osta != 'up':
                inft6_status_in_list = []
                inft6_status_in_list = NetcheckCommon.append2list(inft6_status_in_list,
                                                                 device, intf, descript)
                if 'enabled' in ipv6 and len(ipv6) > 1:
                    cidr = [cidr for cidr, value in ipv6.items()]
                    inft6_status_in_list.append(cidr[:-1])
                    inft6_status_out_list.append(inft6_status_in_list)
                elif 'enabled' not in ipv6:
                    cidr = [cidr for cidr, value in ipv6.items()]
                    inft6_status_in_list.append(cidr)
                    inft6_status_out_list.append(inft6_status_in_list)
               
        if crc_info_out_list:
            self.crc_info_out_list = crc_info_out_list
            aetest.loop.mark(self.crc_check,
                             name = (item[1] for item in self.crc_info_out_list))
        if discard_info_out_list:
            self.discard_info_out_list = discard_info_out_list
            aetest.loop.mark(self.discards_check, 
                             name = (item[1] for item in self.discard_info_out_list))
        if error_info_out_list:
            self.error_info_out_list = error_info_out_list
            aetest.loop.mark(self.error_check,
                             name = (item[1] for item in self.error_info_out_list))
        if dupl_info_out_list:
            self.dupl_info_out_list = dupl_info_out_list
            aetest.loop.mark(self.duplex_check,
                             name = (item[1] for item in self.dupl_info_out_list))
        if mtu_info_out_list:
            self.mtu_info_out_list = mtu_info_out_list
            aetest.loop.mark(self.mtu_check,
                             name = (item[1] for item in self.mtu_info_out_list))
        if inft_status_out_list:
            self.inft_status_out_list = inft_status_out_list
            aetest.loop.mark(self.ipv4_intf_check,
                             name = (item[1] for item in self.inft_status_out_list))
        if inft6_status_out_list:
            self.inft6_status_out_list = inft6_status_out_list
            aetest.loop.mark(self.ipv6_intf_check,
                             name = (item[1] for item in self.inft6_status_out_list))                            
        if lag_no_mem_out_list:
            self.lag_no_mem_out_list = lag_no_mem_out_list
            aetest.loop.mark(self.LAG_member_check,
                             name = (item[1] for item in self.lag_no_mem_out_list))
        if lag_mem_down_out_list:
           self.lag_mem_down_out_list = lag_mem_down_out_list
           aetest.loop.mark(self.LAG_intf_oper_check,
                            name = (item[1] for item in self.lag_mem_down_out_list))

    # you may have N tests within each testcase
    # as long as each bears a unique method name
    # this is just an example
    @aetest.test
    def crc_check(self, name = 'none'):
        '''
        
        Check for CRC counters.         

        '''
        try:
           if self.crc_info_out_list:
               for item_crc in self.crc_info_out_list:
                    if item_crc[1] == name:
                        self.failed('%s Description %s CRC count %s, count cleared %s'
                                    %(item_crc[1], item_crc[2], item_crc[4], item_crc[3]))
        except AttributeError:
            self.passed('no interface CRC above threshold')

    @aetest.test
    def discards_check(self, name = 'none'):
        '''
        
        Check for in/out Discard counters.        

        '''
        try:
           if self.discard_info_out_list:
               for item_disc in self.discard_info_out_list:
                    if item_disc[1] == name:
                        self.failed('%s Description %s has %s %s' 
                                    %(item_disc[1], item_disc[2], item_disc[3], item_disc[4]))
        except AttributeError:
            self.passed('No Interface Discards Detected')

    @aetest.test
    def error_check(self, name = 'none'):
        '''
         
        Check for in/out Error counter.

        '''
        try:
            if self.error_info_out_list:
                for item_erro in self.error_info_out_list:
                    if len(item_erro) > 5:
                        if item_erro[3] != '0' or item_erro[5] != '0':
                            if item_erro[1] == name:
                                self.failed('%s Description %s has interface errors'
                                            %(item_erro[1], item_erro[2] ))
                        elif item_erro[3] != '0':
                            if item_erro[1] == name:
                                self.failed('%s Description %s has interface errors'
                                            %(item_erro[1], item_erro[2] ))
        except AttributeError:
            self.passed('No Interface Errors Detected')
                

    @aetest.test
    def duplex_check(self, name = 'none'):
        '''
 
        Interface Duplex Check.    
 
        '''
        try:
            if self.dupl_info_out_list:
                for item_duplx in self.dupl_info_out_list:
                    if item_duplx[1] == name:
                        self.failed('%s Description %s shows %s duplex'
                                    %(item_duplx[1], item_duplx[2], item_duplx[3]))
        except AttributeError:
            self.passed('no half duplex interfaces detected')
  
    @aetest.test
    def LAG_member_check(self, name = 'none'):
        '''

        Link Aggregation Member Interface association check.

        '''
        try:
            if self.lag_no_mem_out_list:
                for item_inft in self.lag_no_mem_out_list:
                    if item_inft[1] == name:
                        self.failed('%s has no member interface configured'
                                    %(item_inft[1]))
        except AttributeError:
            self.passed('No Memberless Link Aggregation Interfaces discovered')

    @aetest.test
    def mtu_check(self, name = 'none'):
        '''
        
        MTU check against MTU documented in topology interface section. 
        
        '''
        try:
            if self.mtu_info_out_list:
                for item_inft in self.mtu_info_out_list:
                    if item_inft[1] == name:
                        self.failed('Interface %s Description: %s MTU Mismatch, Documented value %s vs Configured value %s'
                                    %(item_inft[1], item_inft[2], item_inft[3], item_inft[4]))
        except AttributeError:
            self.passed('No MTU Mismatch detected')

    @aetest.test
    def LAG_intf_oper_check(self, name = 'none'):
        '''
 
        Link Aggregation Member Operation Status Check 

        '''
        try:
            if self.lag_mem_down_out_list:
                for item_inft in self.lag_mem_down_out_list:
                    if item_inft[1] == name:
                        self.failed('Interface %s Description: %s Member of %s is Down'
                                    %(item_inft[1], item_inft[2], item_inft[3]))
        except AttributeError:
            self.passed('No Down Members of Port Channel Detected')

    @aetest.test
    def ipv4_intf_check(self, name = 'none'):
        '''
         
        Operation status for Interface with IPv4 Configured.
  
        '''
        try:
            if self.inft_status_out_list:
                for item_inft in self.inft_status_out_list:
                    if item_inft[1] == name:
                        self.failed('%s Description %s IPv4 %s is Down' 
                                    %(item_inft[1], item_inft[2], item_inft[3:]))
        except AttributeError:
            self.passed('All Interfaces with IPv4 Configured are status UP')
 
    @aetest.test
    def ipv6_intf_check(self, name = 'none'):
        '''
       
        Operation status for Interface with IPv6 Configured.     

        '''
        try:
            if self.inft6_status_out_list:
                for item_inft in self.inft6_status_out_list:
                     self.failed('%s Description %s IPv6 %s is Down'
                                 %(item_inft[1], item_inft[2], item_inft[3:]))
        except AttributeError:
            self.passed('All Interfaces with IPv6 Configured are status UP')

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
