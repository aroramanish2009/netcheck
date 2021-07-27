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
sys.path.insert(0, '../lib/common')
import NetcheckCommon

from pyats import aetest

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
            dupl_info_in_list = []
            dupl_info_in_list = NetcheckCommon.append2list(dupl_info_in_list,
                                                           device, intf, descript)
            if duplex_mode and duplex_mode == 'half':
                dupl_info_in_list.append(duplex_mode)
                dupl_info_out_list.append(dupl_info_in_list)    
            #IPv4 Interface Operational Status
            ipv4 = data.get('ipv4')
            osta = data.get('oper_status')
            if ipv4 and osta != 'up':
                inft_status_in_list = []
                inft_status_in_list = NetcheckCommon.append2list(inft_status_in_list,
                                                                 device, intf, descript)
                for cidr, value in ipv4.items():
                    inft_status_in_list.append(cidr)
                inft_status_out_list.append(inft_status_in_list)
               
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
        if inft_status_out_list:
           self.inft_status_out_list = inft_status_out_list
           aetest.loop.mark(self.ipv4_intf_check,
                            name = (item[1] for item in self.inft_status_out_list))

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

