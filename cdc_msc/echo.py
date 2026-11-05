import serial

s = serial.Serial('/dev/cu.usbmodem1101', 115200, timeout=2)
s.dtr = True          # without this, the board won't echo
s.write(b'hello world!\n')
print(s.read(100))
