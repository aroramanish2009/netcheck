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
        else:
            self.failed('Cannot learn %s interface information: '
                        'did not establish connectivity to device'
                        % device.name)
        
        #Create simple datasets for test cases.
        crc_info_out_list = []
        discard_info_out_list = []
        error_info_out_list = []
        for intf, data in self.interface_info.info.items():
            counters = data.get('counters')
            descript = data.get('description')
            if counters:
                crc_info_in_list = []
                crc_info_in_list.append(device)
                crc_info_in_list.append(intf)
                crc_info_in_list.append(descript)
                if 'in_crc_errors' in counters:
                    crc_info_in_list.append(counters['last_clear'])
                    crc_info_in_list.append(str(counters['in_crc_errors']))
                else:
                    crc_info_in_list.extend(['none', '0'])
                crc_info_out_list.append(crc_info_in_list)
                discard_info_in_list = []
                discard_info_in_list.append(device)
                discard_info_in_list.append(intf)
                discard_info_in_list.append(descript)
                if 'out_discard' in counters:
                    discard_info_in_list.append(str(counters['out_discard']))
                    discard_info_in_list.append('out_discard')
                elif 'in_discards' in counters:
                    discard_info_in_list.append(str(counters['in_discards']))
                    discard_info_in_list.append('in_discards')
                else:
                    discard_info_in_list.extend(['0', 'N/A'])
                discard_info_out_list.append(discard_info_in_list)
                error_info_in_list = []
                error_info_in_list.append(device)
                error_info_in_list.append(intf)
                error_info_in_list.append(descript)
                if 'in_errors' in counters or 'out_errors' in counters:
                    try:
                        error_info_in_list.append(str(counters['in_errors']))
                        error_info_in_list.append('in_errors')
                        error_info_in_list.append(str(counters['out_errors']))
                        error_info_in_list.append('out_errors')
                    except:
                        error_info_in_list.append(str(counters['out_errors']))
                        error_info_in_list.append('out_errors')
                else:
                    error_info_in_list.extend(['0', 'N/A'])
                error_info_out_list.append(error_info_in_list)

            duplex_mode = data.get('duplex_mode')
               
        self.crc_info_out_list = crc_info_out_list
        aetest.loop.mark(self.crc_check,
                         name = (item[1] for item in self.crc_info_out_list))
        self.discard_info_out_list = discard_info_out_list
        aetest.loop.mark(self.discards_check, 
                         name = (item[1] for item in self.discard_info_out_list))
        self.error_info_out_list = error_info_out_list
        aetest.loop.mark(self.error_check,
                         name = (item[1] for item in self.error_info_out_list))

    # you may have N tests within each testcase
    # as long as each bears a unique method name
    # this is just an example
    @aetest.test
    def crc_check(self, name):
        '''
        
        Check for CRC counters.         

        '''
        for item_crc in self.crc_info_out_list:
            if name in item_crc and item_crc[4] != '0':
                self.failed('%s Description %s CRC count %s, count cleared %s'
                            %(name, item_crc[2], item_crc[4], item_crc[3]))
            else:
                self.passed('no interface CRC above threshold')

    @aetest.test
    def discards_check(self, name):
        '''
        
        Check for in/out Discard counters.        

        '''
        for item_disc in self.discard_info_out_list:
            if name in item_disc and item_disc[3] != '0':
                self.failed('%s Description %s has %s %s' 
                            %(name, item_disc[2], item_disc[3], item_disc[4]))
            else:
                self.passed('no interface discards')

    @aetest.test
    def error_check(self):
        '''
         
        Check for in/out Error counter.

        '''
        for item_erro in self.error_info_out_list:
            if len(item_erro) > 5:
                if item_erro[3] != '0' or item_erro[5] != '0':
                    self.failed('%s Description %s has interface errors'
                                %(item_disc[1], item_disc[2] ))
                elif item_erro[3] != '0':
                 self.failed('%s Description %s has interface errors'
                             %(item_disc[1], item_disc[2] ))
                else:
                    self.passed('no interface errors')

                

    @aetest.test
    def duplex_check(self):
        pass

    @aetest.test
    def oper_status_check(self):
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

