#######################################################################
### To use this tool you must be in the same directory as the image ###
#######################################################################

import os
import binascii
import re
from functools import partial
import textwrap
import struct
from optparse import OptionParser

file_system_type = { '0x0' : "Empty", '0x1' : "FAT12", '0x2' : "XENIX root", '0x3' : "XENIX usr",
               '0x4' : "FAT16", '0x5' : "Extended", '0x6' : "FAT16B", '0x7' : "NTFS", '0x8' : "AIX" ,
               '0x9' : "AIX Bootable" , '0xa' : "OS/2 Boot" , '0xb' : "Win95 FAT32" , '0xc' : "Win95 FAT32" ,
               '0xd' : "Reserved" , '0xe' : "Win95 FAT16" , '0xf' : "Win95 Ext" , '0x10' : "OPUS" ,
               '0x11' : "FAT12 Hidden" , '0x12' : "Compaq Diag" , '0x13' : "N/A" , '0x14' : "FAT16 Hidden" ,
               '0x15' : "Extended Hidden" , '0x16' : "FAT16 Hidden" , '0x17' : "NTFS Hidden" , '0x18' : "AST" ,
               '0x19' : "Willowtech" , '0x1a' : "N/A" , '0x1b' : "Hidden FAT32" , '0x1c' : "Hidden FAT32X" ,
               '0x1d' : "N/A" , '0x1e' : "Hidden FAT16X", '0x83' : 'Unrecognized Filesystem Type' }

parser = OptionParser(usage='usage: python3 %prog -i <image>')
parser.add_option('-i', '--image', dest = 'image')
(options, args) = parser.parse_args()
if not options.image:
    parser.error('Image not defined')
else:
    image = options.image

op_sys = os.name

if op_sys == 'nt': #if windows
#open file in binary
    image = os.getcwd() + '\\' + image
else:
    image = os.getcwd() + '/' + image #if Linux or MAC

image_bin = open(image, 'rb').read(512)

#convert to hex
add_spaces = partial(re.compile(b'(..)').sub, br'\1 ')
image_hex = (binascii.hexlify(image_bin).decode('utf-8'))
image_hex_with_spaces = (add_spaces(binascii.hexlify(image_bin))).decode('utf-8')
lines = textwrap.wrap(image_hex_with_spaces, width = 64)

#Parse partition contents
def parse_partition_content(decode):
    byte_1 = struct.pack("<B", decode[0])
    byte_2 = struct.pack("<B", decode[1])
    byte_3 = struct.pack("<B", decode[2])
    byte_4 = struct.pack("<B", decode[3])
    combine_bytes = byte_1 + byte_2 + byte_3 + byte_4
    partition_data = struct.unpack("<L",combine_bytes)[0]
    return partition_data


#Only execute rest of the code if sector is a MBR
if image_hex[-4:] == '55aa':
    print('-' * 18 + 'MBR SECTOR (1st 512 Bytes)' + '-' * 18)
    for line in lines:
        print(str(line) + '\n')
    try:
        disk_sig = struct.unpack("<L", image_bin[440:444])
        print ("Disk Signature: {} \n".format(hex(disk_sig[0])))

        partitions = [struct.unpack('<BBBBBBBBBBBBBBBB', image_bin[446:462]), struct.unpack('<BBBBBBBBBBBBBBBB', image_bin[462:478]), struct.unpack('<BBBBBBBBBBBBBBBB', image_bin[478:494]), 
                      struct.unpack('<BBBBBBBBBBBBBBBB', image_bin[494:510])]

        for index, partition in enumerate(partitions, start = 1):
            print('-' * 25 + 'Partition {}'.format(index) + '-' * 26)
            filesystem_descriptor = hex(partition[4])
            if filesystem_descriptor != '0x0':
                try:
                    print ("Filesystem type: {}".format(file_system_type[filesystem_descriptor]))
                    if hex(partition[0]) == '0x80':
                        print('Partition is bootable')
                    else:
                        print('Partition is not bootable')
                    print('Start head value: {}'.format(partition[1]))
                    print('End head value: {}'.format(partition[5]))
                    print('Start sector value: {}'.format(partition[2]))
                    print('End sector value: {}'.format(partition[6]))
                    print('Start cylinder value: {}'.format(partition[3]))
                    print('End cylinder value: {}'.format(partition[7]))
                    print('Partition starts at sector: {}'.format(parse_partition_content(partition[8:12])))
                    print('Partition length: {}'.format(parse_partition_content(partition[12:16])))
                except:
                    print('Error parsing partitions')
            else:
                print('Empty Partition')
    except Exception as e:
        print('Error Parsing MBR sector. Error: ' + str(e))
else:
    print(CRED + 'Not an MBR sector' + CEND)
    print('-' * 18 + 'MBR SECTOR (1st 512 Bytes)' + '-' * 18)
    for line in lines:
        print(str(line) + '\n')