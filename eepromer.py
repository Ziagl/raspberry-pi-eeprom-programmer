import wiringpi
import time

SHIFT_DATA = 0
SHIFT_CLK = 1
SHIFT_LATCH = 2
WRITE_EN = 27

EEPROM_DATA = [3, 4, 5, 6, 21, 22, 26, 25]

INPUT = 0
OUTPUT = 1
MSBFIRST = 1
LOW = 0
HIGH = 1

def setAddress(address, outputEnable):
	wiringpi.shiftOut(SHIFT_DATA, SHIFT_CLK, MSBFIRST, ((address >> 8) | (0x00 if outputEnable  else 0x80)))
	wiringpi.shiftOut(SHIFT_DATA, SHIFT_CLK, MSBFIRST, (address & 255))

	wiringpi.digitalWrite(SHIFT_LATCH, LOW)
	wiringpi.digitalWrite(SHIFT_LATCH, HIGH)
	wiringpi.digitalWrite(SHIFT_LATCH, LOW)

def readEEPROM(address):
	for pin in EEPROM_DATA:
		wiringpi.pinMode(pin, INPUT)
	setAddress(address, True)
	data = 0
	for pin in reversed(EEPROM_DATA):
		data = (data << 1) + wiringpi.digitalRead(pin)
	return data

def writeEEPROM(address, data):
	for pin in EEPROM_DATA:
		wiringpi.pinMode(pin, OUTPUT)
	setAddress(address, False)
	for pin in EEPROM_DATA:
		wiringpi.digitalWrite(pin, data & 1)
		data = data >> 1
	wiringpi.digitalWrite(WRITE_EN, LOW)
	time.sleep(0.0000001)
	wiringpi.digitalWrite(WRITE_EN, HIGH)
	time.sleep(0.01)

def printContents():
	for base in range(0, 256, 16):
	#for base in range(0, 2048, 16):        #if you want to print whole storage of AT28C16
		data = [0] * 16
		for offset in range(0, 16):
			data[offset] = readEEPROM(base + offset)
		buf = "%03x: %02x %02x %02x %02x %02x %02x %02x %02x   %02x %02x %02x %02x %02x %02x %02x %02x" % (base, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11], data[12], data[13], data[14], data[15])
		print buf

data = [0x81, 0xcf, 0x92, 0x86, 0xcc, 0xa4, 0xa0, 0x8f, 0x80, 0x84, 0x88, 0xe0, 0xb1, 0xc2, 0xb0, 0xb8]

def setup():
	wiringpi.wiringPiSetup()
	wiringpi.pinMode(SHIFT_DATA, OUTPUT)
	wiringpi.pinMode(SHIFT_CLK, OUTPUT)
	wiringpi.pinMode(SHIFT_LATCH, OUTPUT)
	
	wiringpi.digitalWrite(WRITE_EN, HIGH)
	wiringpi.pinMode(WRITE_EN, OUTPUT)

        #erase entire EEPROM
	print "Erasing EEPROM"
	for address in range(2048):
                writeEEPROM(address, 0xff)
        print "done"

        #program data bytes
        print "Programming EEPROM"
        for address in range(len(data)):
                writeEEPROM(address, data[address])
        print "done"

        #read and print out the contents of the EEPROM
        print "Reading EEPROM"
	printContents()

setup()
