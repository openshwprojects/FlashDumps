#!/usr/bin/env python
# RTL872xDx ROM Bootloader Utility Ver 05.11.2020
# Created on: 10.10.2017
# Author: pvvx
#

import sys
import signal
import struct
import serial
import platform
import time
import argparse
import os
import io
import binascii
#import numpy as np

#define	SOH			0x01		/* Start of header */
#define	STX			0x02		/* Start of header XModem-1K */
#define	EOT			0x04		/* End of transmission */
#define	ACK			0x06		/* Acknowledge */
#define	NAK			0x15		/* Not acknowledge */
#define	CAN			0x18		/* Cancel */
#define	ESC			0x1b		/* User Break */

# Protocol bytes
SOH = b'\x01' # Start of header
STX = b'\x02' # Start of header XModem-1K
EOT = b'\x04' # End of transmission
ACK = b'\x06' # Acknowledge
DLE = b'\x10' #
NAK = b'\x15' # Not acknowledge
CAN = b'\x18' # Cancel
ESC = b'\x1b' # User Break (End xmodem mode (write RAM/Flash mode))
# added by Realtek
CMD_USB	 = b'\x05'	# UART Set Baud
CMD_XMD	 = b'\x07'	# Go xmodem mode (write RAM/Flash mode)
CMD_EFS	 = b'\x17'	# Erase Flash Sectors
CMD_RBF	 = b'\x19'	# Read Block Flash
CMD_RBF2 = b'\x20'	# Read Block Flash
CMD_ABRT = b'\x1B'	# End xmodem mode (write RAM/Flash mode)
CMD_GFS	 = b'\x21'	# FLASH Read Status Register
CMD_SFS	 = b'\x26'	# FLASH Write Status Register
CMD_CRC	 = b'\x27'	# Check Flash write checksum
CMD_WWA	 = b'\x29'	# Write dword <addr, 4 byte>,<dword, 4 byte> -> 0x06
CMD_RWA	 = b'\x31'	# Read dword <addr, 4 byte> -> 0x31,<dword, 4 byte>,  0x15
CMD_VER	 = b'\x33'	# Read rom code version(02/03/04...)

# Default baudrate
COMPORT_DEF_BAUD_RATE = 115200

RTL_READ_BLOCK_SIZE = 1024
RTL_FLASH_SECTOR_SIZE = 4096

RTLZ_FLOADER = 'imgtool_flashloader_amebad.bin'


def signal_handler(signal, frame):
	print()
	print('Keyboard Break!')
	sys.exit(0)
''' class RTL xModem '''
class RTLXMD:

	def __init__(self, port=0, baud=COMPORT_DEF_BAUD_RATE, timeout=0.2):
		try:
			self._port = serial.Serial(port, baud)
			self._port.timeout = timeout
			self.timeout = timeout
			self._port.reset_input_buffer()
			self._port.reset_output_buffer()
		except:
			print('Error: Open %s, %d baud!' % (port, baud))
			sys.exit(-1)

	def WaitResp(self, code = ACK):
		count = 10
		for i in range(count):
			char = self._port.read(1)
			if char:
				if char == code:
					return True
				#elif char != NAK:
				#	print(hex(char[0]))
				#	return False
			else:
				return None
		return False

	def WriteCmd(self, cmd, ok = ACK):
		if not self._port.write(cmd):
			return False
		return self.WaitResp(ok)
	'''
	def WaitNAK(self):
		chr_count = 10
		while chr_count:
			char = self._port.read(1)
			if char:
				if char == NAK:
					return True
			chr_count -= 1
		return False
	'''
	def GetFlashStatus(self, num = 0):
		blk = CMD_GFS+b'\x05\x01'
		if num == 1:
			blk = CMD_GFS+b'\x35\x01'
		elif num == 2:
			blk = CMD_GFS+b'\x15\x01'
		if not self.WriteCmd(blk, CMD_GFS):
			return None
		return self._port.read(1)

	def SetComBaud(self, baud):
		try:
			self._port.close()
			self._port.baudrate = baud
			self._port.open()
			self._port.timeout = self.timeout
			time.sleep(0.05)
			self._port.reset_output_buffer()
			self._port.reset_input_buffer()
		except:
			print('Error: ReOpen %s, %d baud!' % (port, baud))
			sys.exit(-1)
		return True

	def SetBaud(self, baud):
		br = [115200, 128000, 153600, 230400, 380400, 460800, 500000, 921600, 1000000, 1382400, 1444400, 1500000]
		x = 0x0d
		if baud > 1500000:
			baud = 1500000
		for el in br:
			if el >= baud:
				baud = el
				break
			x += 1
		if self._port.baudrate != baud:
			print('Set baudrate', baud)
			if not self.WriteCmd(struct.pack('<BB', ord(CMD_USB), x)):
				return False
			return self.SetComBaud(baud)
		return True

	def RestoreBaud(self):
		if self._port.baudrate != COMPORT_DEF_BAUD_RATE:
			return self.SetBaud(COMPORT_DEF_BAUD_RATE)
		return True

	def SetFlashStatus(self, status, num = 0):
		blk = CMD_SFS+b'\x01\x01'+struct.pack('<B', status&0xff)
		if num == 1:
			blk = CMD_SFS+b'\x31\x01'+struct.pack('<B', status&0xff)
		elif num == 2:
			blk = CMD_SFS+b'\x11\x01'+struct.pack('<B', status&0xff)
		if self.WriteCmd(blk):
			return self.GetFlashStatus()
		return None

	def ReadRegs(self, offset = 0x00080000, size = 0x10000): # KM0 SRAM 64K
		out = []
		while size > 0:
			if not self._port.write(struct.pack('<BI', ord(CMD_RWA), offset)):
				print('Error Write to COM Port!')
				return False
			if not self.WaitResp(CMD_RWA):
				print('Error read data head id!')
				return False
			# 0x31,<dword, 4 byte>, 0x15
			data = self._port.read(5)
			if data and len(data) == 5 and data[4] == ord(NAK):
				out += data[:4]
			else:
				return None
			size -= 4
			offset += 4
		return out

	def ReadBlockMem(self, stream, offset = 0x00080000, size = 0x10000): # KM0 SRAM 64K
		while size > 0:
			if not self._port.write(struct.pack('<BI', ord(CMD_RWA), offset)):
				print('Error Write to COM Port!')
				return False
			if not self.WaitResp(CMD_RWA):
				print('Error read data head id!')
				return False
			# 0x31,<dword, 4 byte>, 0x15
			data = self._port.read(5)
			if data and len(data) == 5 and data[4] == ord(NAK):
				stream.write(data[:4])
			else:
				return False
			size -= 4
			offset += 4
		return True

	def ReadBlockFlash(self, stream, offset = 0, size = 0x200000):
		# Read sectors size: 4 block 1024 bytes, else not set ACK!
		count = int((size + RTL_FLASH_SECTOR_SIZE - 1) / RTL_FLASH_SECTOR_SIZE)
		offset &= 0xffffff
		if count < 1 or count > 0x10000 or offset < 0:
			print('Bad parameters!')
			return False
		if not self._port.write(struct.pack('<BHBH', ord(CMD_RBF2), offset & 0xffff, (offset >> 16) & 0xff, count)):
			print('Error Write to COM Port!')
			return False
		count *= 4 # Xmodem Read size 1024 bytes
		for i in range(count):
			if (i & 63) == 0:
				print('Read block at 0x%06x...' % (offset), end = '')
			while True:
				if not self.WaitResp(STX):
					print('Error read block head id!')
					return False
				data = self._port.read(2)
				if len(data) == 2 and (data[0] == (i+1)&0xff) and (data[0]^0xff == data[1]):
					break
				else:
					print('Error read block head!', binascii.hexlify(data))
					return False
			data = self._port.read(RTL_READ_BLOCK_SIZE+1)
			if data and len(data) == RTL_READ_BLOCK_SIZE+1:
				if data[RTL_READ_BLOCK_SIZE] != self.calc_checksum(data[:RTL_READ_BLOCK_SIZE]):
					print('Bad Checksum!')
					self.WriteCmd(CAN)
					return False
				if size > RTL_READ_BLOCK_SIZE:
					if not self._port.write(ACK):
						print('Error Write to COM Port!')
						return False
					stream.write(data[:RTL_READ_BLOCK_SIZE])
				else:
					stream.write(data[:size])
					self.WriteCmd(CAN)
					if (i & 63) == 0:
						print('ok')
					return True
			else:
				return False
			size -= RTL_READ_BLOCK_SIZE
			offset += RTL_READ_BLOCK_SIZE
			if (i & 63) == 0:
				print('ok')
		return True

	def Connect(self):
		# issue reset-to-bootloader:
		# RTS = either RESET (both active low = chip in reset)
		self._port.setDTR(False)
		self._port.setRTS(True)
		time.sleep(0.05)
		self._port.setDTR(True)
		self._port.setRTS(False)
		time.sleep(0.05)
		self._port.setDTR(False)
		return True

	def EraseSectorsFlash(self, offset = 0, size = 0x200000):
		count = int((size + RTL_FLASH_SECTOR_SIZE - 1) / RTL_FLASH_SECTOR_SIZE)
		offset &= 0xfff000
		if count > 0 and count < 0x10000 and offset >= 0: # 1 byte .. 16 Mbytes
			for i in range(count):
				if not self.WriteCmd(struct.pack('<BHBH', ord(CMD_EFS), offset & 0xffff, (offset >> 16) & 0xff, 1)):
					return False
				offset += RTL_FLASH_SECTOR_SIZE
		else:
			print('Bad parameters!')
			return False
		return True
	'''
	def calc_checksum32(self, data):
		self.chk32 = sum(np.frombuffer(data, dtype='<i4') + self.chk32) & 0xffffffff
		return self.chk32
	'''
	def calc_checksum(self, data, checksum=0):
		#if platform.python_version_tuple() >= ('3', '0', '0'):
		return (sum(data) + checksum) & 0xff
		#else:
		#	return (sum(map(ord, data)) + checksum) & 0xff

	def send_xmodem(self, stream, offset, size, retry = 3):
		if not self.WriteCmd(CMD_XMD):
			return False
		self.chk32 = 0
		sequence = 1
		while size > 0:
			if size <= 128:
				packet_size = 128
				cmd = SOH
			else:
				packet_size = 1024
				cmd = STX
			
			rdsize = packet_size
			if size < rdsize:
				rdsize = size
			data = stream.read(rdsize)
			if not data: # end of stream
				print('send: at EOF')
				return False
			# calc_checksum32(data)
			data = data.ljust(packet_size, b'\xFF')
			pkt = struct.pack('<BBBI', ord(cmd), sequence, 0xff - sequence, offset) + data
			crc = self.calc_checksum(pkt[3:])
			pkt += struct.pack('<B', crc)
			error_count = 0
			while True:
				if self.WriteCmd(pkt):
					sequence = (sequence + 1) % 0x100
					offset += packet_size
					size -= rdsize
					break
				else:
					error_count += 1
					if error_count > retry:
						return False
		return self.WriteCmd(EOT) # End of transmission # if write SRAM -> (*0x00082000)()

	def WriteBlockMem(self, stream, offset = 0x00082000, size = 0x1000, retry = 3):
		return self.send_xmodem(stream, offset, size, retry)

	def WriteBlockFlash(self, stream, offset = 0x08000000, size = 0x200000, retry = 3):
		return self.send_xmodem(stream, offset, size, retry)

	def FlashWrChkSum(self, offset = 0, size = 0x100):
		if not self.WriteCmd(struct.pack('<BBHHB', ord(CMD_CRC), offset & 0xff, (offset >> 8) & 0xffff,  size & 0xffff,  (size >> 16) & 0xff), CMD_CRC):
			return None
		data = self._port.read(4)
		if data == None or len(data) != 4:
			return None
		return struct.unpack('<I', data)

	def Floader(self, baud):
		if not self.SetBaud(baud):
			print('Error Set Baud!')
			return False
		data = rtl.ReadRegs(0x00082000,4)
		if not data:
			print('Error Read!')
			self.RestoreBaud()
			return False
		#print('Read regs:', data)
		if data != [33, 32, 8, 0]:
			stream = open(RTLZ_FLOADER, 'rb')
			size = os.path.getsize(RTLZ_FLOADER)
			if size < 1:
				stream.close
				print('Error: File size = 0!')
				self.RestoreBaud()
				return False
			offset = 0x00082000
			print('Write SRAM at 0x%08x to 0x%08x from file: %s' % (offset, offset + size, RTLZ_FLOADER))
			if not self.WriteBlockMem(stream, offset, size):
				stream.close
				print('Error Write!')
				self.RestoreBaud()
				return False
			stream.close
			rtl.SetComBaud(COMPORT_DEF_BAUD_RATE)
			if not rtl.SetBaud(baud):
				print('Error Set Baud!')
				return False
		return True

def arg_auto_int(x):
	return int(x, 0)

if __name__ == '__main__':
	signal.signal(signal.SIGINT, signal_handler)
	parser = argparse.ArgumentParser(description='RT872xDx ROM Bootloader Utility', prog='rtlptool')

	parser.add_argument(
			'--port', '-p',
			help='Serial port device',
			default='COM0')
	'''
	parser.add_argument(
			'--go','-g', action="store_true",
			help='Run after performing the operation')
	'''
	parser.add_argument(
		'-b', '--baud',
		help='UART Baud Rate (default: '+str(COMPORT_DEF_BAUD_RATE)+')',
		type=arg_auto_int,
		default=COMPORT_DEF_BAUD_RATE)

	subparsers = parser.add_subparsers(
			dest='operation',
			help='Run rtlbtool {command} -h for additional help')

	parser_read_flash = subparsers.add_parser(
			'rf',
			help='Read Flash data to binary file')
	parser_read_flash.add_argument('address', help='Start address', type=arg_auto_int)
	parser_read_flash.add_argument('size', help='Size of region', type=arg_auto_int)
	parser_read_flash.add_argument('filename', help='Name of binary file')

	parser_read_reg = subparsers.add_parser(
			'rr',
			help='Read REGs or RAM to binary file')
	parser_read_reg.add_argument('address', help='Start address', type=arg_auto_int)
	parser_read_reg.add_argument('size', help='Size of region', type=arg_auto_int)
	parser_read_reg.add_argument('filename', help='Name of binary file')

	parser_read_mem = subparsers.add_parser(
			'rm',
			help='Read SRAM to binary file')
	parser_read_mem.add_argument('address', help='Start address', type=arg_auto_int)
	parser_read_mem.add_argument('size', help='Size of region', type=arg_auto_int)
	parser_read_mem.add_argument('filename', help='Name of binary file')

	parser_write_flash = subparsers.add_parser(
			'wf',
			help='Write a binary file to Flash data')
	parser_write_flash.add_argument('address', help='Start address', type=arg_auto_int)
	parser_write_flash.add_argument('filename', help='Name of binary file')

	parser_write_reg = subparsers.add_parser(
			'wr',
			help='Write a binary file to REGs or RAM')
	parser_write_reg.add_argument('address', help='Start address', type=arg_auto_int)
	parser_write_reg.add_argument('filename', help='Name of binary file')

	parser_write_mem = subparsers.add_parser(
			'wm',
			help='Write a binary file to SRAM')
	parser_write_mem.add_argument('address', help='Start address', type=arg_auto_int)
	parser_write_mem.add_argument('filename', help='Name of binary file')

	parser_erase_flash = subparsers.add_parser(
			'es',
			help='Erase Sectors Flash')
	parser_erase_flash.add_argument('address', help='Start address', type=arg_auto_int)
	parser_erase_flash.add_argument('size', help='Size of region', type=arg_auto_int)

	parser_chk_flash = subparsers.add_parser(
			'cf',
			help='Checksum block in Flash')
	parser_chk_flash.add_argument('address', help='Start address', type=arg_auto_int)
	parser_chk_flash.add_argument('size', help='Size of region', type=arg_auto_int)

	parser_get_status_flash = subparsers.add_parser(
			'gf',
			help='Get Flash Status registers')

	parser_set_status_flash = subparsers.add_parser(
			'sf',
			help='Set Flash Status register')
	parser_set_status_flash.add_argument('number', help='Number 0, 1, 2', type=arg_auto_int)
	parser_set_status_flash.add_argument('value', help='Value', type=arg_auto_int)
	'''
	parser_boot_flash = subparsers.add_parser(
			'bf',
			help='Start boot flash')
	parser_set_status_flash = subparsers.add_parser(
			'gm',
			help='Go ROM Monitor')
	'''
	args = parser.parse_args()
	rtl = RTLXMD(args.port)
	print('Connecting...')
	if rtl.Connect():
		# Write Flash
		if args.operation == 'wf':
			if not rtl.SetFlashStatus(0,0):
				print('Error: Set Flash Status!')
				sys.exit(-1)
			stream = open(args.filename, 'rb')
			size = os.path.getsize(args.filename)
			if size < 1:
				stream.close
				print('Error: File size = 0!')
				sys.exit(-1)
			if not rtl.Floader(args.baud):
				stream.close
				rtl.RestoreBaud()
				sys.exit(-1)
			count = int((size + RTL_FLASH_SECTOR_SIZE - 1) / RTL_FLASH_SECTOR_SIZE)
			esize = int(count * RTL_FLASH_SECTOR_SIZE)
			offset = args.address & 0xfff000
			print('Erase Flash %d sectors, data from 0x%08x to 0x%08x' % (count, offset, offset + esize))
			if not rtl.EraseSectorsFlash(offset, size):
				print('Error: Erase Flash sectors!')
				sys.exit(-2)
			offset = args.address & 0x00ffffff
			offset |= 0x08000000
			print('Write Flash data 0x%08x to 0x%08x from file: %s' % (offset, offset + size, args.filename))
			if not rtl.WriteBlockFlash(stream, offset, size):
				stream.close
				print('Error: Write Flash!')
				rtl.RestoreBaud()
				sys.exit(-2)
			stream.close
			chk = rtl.FlashWrChkSum(offset, size)
			if chk == None: 
				print('Flash block checksum retrieval error!')
				rtl.RestoreBaud()
				sys.exit(-2)
			#print('Checksum of the written block in Flash: 0x%08x | 0x%08x' % (chk[0], rtl.chk32))
			print('Checksum of the written block in Flash: 0x%08x' % (chk[0]))
			rtl.RestoreBaud()
		# Read Flash
		elif args.operation == 'rf':
			if args.size < 0 or args.address < 0 or args.address + args.size > 0x1000000:
				print('Bad parameters!')
				sys.exit(-1)
			if not rtl.Floader(args.baud):
				sys.exit(-1)
			offset = args.address & 0x00ffffff
			#offset |= 0x08000000
			print('Read Flash data from 0x%08x to 0x%08x in file: %s' % (offset, offset + args.size, args.filename))
			stream = open(args.filename, 'wb')
			if not rtl.ReadBlockFlash(stream, offset, args.size):
				stream.close
				rtl.RestoreBaud()
				sys.exit(-2)
			stream.close
			rtl.RestoreBaud()
		# Erase Flash
		elif args.operation == 'es':
			count = int((args.size + RTL_FLASH_SECTOR_SIZE - 1) / RTL_FLASH_SECTOR_SIZE)
			size = int(count * RTL_FLASH_SECTOR_SIZE)
			offset = args.address & 0xfff000
			print('Erase Flash %d sectors, data from 0x%08x to 0x%08x' % (count, offset, offset + size))
			if not rtl.EraseSectorsFlash(offset, size):
				print('Error: Erase Flash sectors!')
				sys.exit(-2)
		# Read SRAM | REGs | RAM | ROM
		elif args.operation == 'rm' or args.operation == 'rr':
			if args.size < 0:
				print('Bad parameters!')
				sys.exit(-1)
			if args.size > 0x400:
				if not rtl.SetBaud(args.baud):
					sys.exit(-1)
			if args.size  > 0x00100000:
				args.size = 0x00100000
				print('Size to big! Set size 0x100000.')
			if args.operation == 'rr':
				print('Read REGs or RAM from 0x%08x to 0x%08x in file: %s' % (args.address, args.address+args.size, args.filename))
			else:
				args.address &= 0x000fffff
				args.address |= 0x00080000 # KM0 SRAM
				print('Read SRAM from 0x%08x to 0x%08x in file: %s' % (args.address, args.address+args.size, args.filename))
			stream = open(args.filename, 'wb')
			if not rtl.ReadBlockMem(stream, args.address, args.size):
				stream.close
				print('Error!')
				rtl.RestoreBaud()
				sys.exit(-2)
			stream.close
			rtl.RestoreBaud()
		# Write SRAM | REGs | RAM | ROM
		elif args.operation == 'wm' or args.operation == 'wr':
			stream = open(args.filename, 'rb')
			size = os.path.getsize(args.filename)
			if size < 1:
				stream.close
				print('Error: File size = 0!')
				sys.exit(-1)
			if size > 0x1000:
				if not rtl.SetBaud(args.baud):
					sys.exit(-1)
			if args.operation == 'wm':
				args.address &= 0x000fffff
				args.address |= 0x00080000 # KM0 SRAM
				print('Write SRAM at 0x%08x to 0x%08x from file: %s' % (args.address, args.address + size, args.filename))
			else:
				print('Write REGs or RAM at 0x%08x to 0x%08x from file: %s' % (args.address, args.address + size, args.filename))
			if not rtl.WriteBlockMem(stream, args.address, size):
				stream.close
				print('Error Write!')
				rtl.RestoreBaud()
				sys.exit(-2)
			stream.close
			rtl.RestoreBaud()
		# Get Flash status
		elif args.operation == 'gf':
			if not rtl.Floader(COMPORT_DEF_BAUD_RATE):
				sys.exit(-1)
			fsta = rtl.GetFlashStatus(0)
			if not fsta:
				print('Error: Get Flash Status!')
				sys.exit(-2)
			print('Flash Status (0) Value: 0x%02x' % (ord(fsta)))
			fsta = rtl.GetFlashStatus(1)
			if not fsta:
				print('Error: Get Flash Status!')
				sys.exit(-2)
			print('Flash Status (1) Value: 0x%02x' % (ord(fsta)))
			fsta = rtl.GetFlashStatus(2)
			if not fsta:
				print('Error: Get Flash Status!')
				sys.exit(-2)
			print('Flash Status (2) value: 0x%02x' % (ord(fsta)))

		# Set Flash status
		elif args.operation == 'sf':
			if not rtl.Floader(COMPORT_DEF_BAUD_RATE):
				sys.exit(-1)
			print('Set Flash Status (%d) value: 0x%02x' % (args.number & 3, args.value & 0xFF))
			if rtl.SetFlashStatus(args.value & 0xFF, args.number & 3):
				sys.exit(0)
			print('Error: Set Flash Status!')
			sys.exit(-2)
		# Checksum block in Flash
		elif args.operation == 'cf':
			size = args.size & 0x00ffffff
			offset = args.address & 0x00ffffff
			if size < 1:
				print('Bad parameters!')
				sys.exit(-1)
			chk = rtl.FlashWrChkSum(offset, size)
			if chk == None: 
				print('Flash block checksum retrieval error!')
				sys.exit(-2)
			print('Flash block from 0x%06x with size 0x%06x, Checksum: 0x%08x' % (offset, size, chk[0]))
		'''
		# TODO Boot form Flash
		elif args.operation == 'bf':
			print('BOOT_ROM_FromFlash()...')
			if not rtl.WriteCmd(ESC):
				print('Error!')
				sys.exit(-2)
			print('Done!')
			#rtl._port.close()
			#rtl._port.baudrate = COMPORT_DEF_BAUD_RATE
			#rtl._port.open()
			rtl._port.timeout = 1
			sio = io.TextIOWrapper(io.BufferedRWPair(rtl._port, rtl._port))
			print(sio.readline(),sio.readline(),sio.readline(),sio.readline(),sio.readline())
			sys.exit(0)
		'''
	else:
		print('Failed to connect device on', args.port, '!')
		sys.exit(-2)
	'''
	if args.go: #TODO
		print('BOOT FromFlash...')
		rtl.WriteCmd(ESC)
	'''
	print('Done!')
	sys.exit(0)
