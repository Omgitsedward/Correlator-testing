#Clk Freq = 250 MHz, Input signal freq = 75 Mhz at -6.0 dBm
#Using 12-input SNAP Board w/ RaspberryPi 
#10 stage fft_biplex_real_2x
#4-tap 1024-point polyphase filter bank
#This one will Correlate all 12 inputs at the same time

import corr, struct, numpy as np, matplotlib.pyplot as plt, time

#--------------------------------------------------------------------------------------------------------------------------------------
from argparse import ArgumentParser
p = ArgumentParser(description = 'python noise2.py [options] ')
p.add_argument('host', type = str, default = '10.0.1.217', help = 'Specify the host name')
p.add_argument('-s', '--shift', dest = 'shift', type = int, default = 2047, help = 'set shift value for fft biplex block')
p.add_argument('-l', '--length', dest = 'length', type = int, default = 2e6, help = 'set # of spectra to be accumulated')

args = p.parse_args()
host = args.host
shift = args.shift
length = args.length 

#--------------------------------------------------------------------------------------------------------------------------------------
#Merges real and imaginary parts of fft data into a single number
def splicing(x):
	temp = []
	z = 0
	while z < 2048:
		temp.append(x[z] + x[z+1]*1j)
		z += 2
	return np.asarray(temp)

#Merges real and imaginary parts of Cross Correlation data into a single number
def merge(x,y):
	temp = []
	w = 0
	while w < 512:
		temp.append(x[w] + y[w]*1j)
		w += 1
	return np.asarray(temp)
	
#--------------------------------------------------------------------------------------------------------------------------------------
print "Connecting to Fpga"
s = corr.katcp_wrapper.FpgaClient(host,7147,timeout = 10)
time.sleep(1)

#--------------------------------------------------------------------------------------------------------------------------------------
if s.is_connected():
	print "Connected"
else:
	print "Not connected"

#--------------------------------------------------------------------------------------------------------------------------------------
f = np.linspace(0,1023,1024)
t = np.linspace(0,65535,65536)

#--------------------------------------------------------------------------------------------------------------------------------------
print "Setting Shift value"
s.write_int('shift',shift)
print "Done"

#--------------------------------------------------------------------------------------------------------------------------------------
print "Starting accumulation process"
s.write_int('acc_len',length)

#--------------------------------------------------------------------------------------------------------------------------------------
s.write_int('trig',0)
s.write_int('trig',1)
s.write_int('trig',0)

acc_num = s.read_int('acc_num')
while s.read_int('acc_num') == acc_num:
	time.sleep(0.1)
print acc_num
acc_num = s.read_int('acc_num')
while s.read_int('acc_num') == acc_num:
	time.sleep(0.1)
print acc_num
acc_num = s.read_int('acc_num')
while s.read_int('acc_num') == acc_num:
	time.sleep(0.1)
print acc_num
print "Done"

#--------------------------------------------------------------------------------------------------------------------------------------
overflow = s.read_int('overflow')
print overflow

#--------------------------------------------------------------------------------------------------------------------------------------
#Reading Data from BRAM Blocks
fft0 = np.asarray(struct.unpack('>2048l',s.read('fft_data0',8192)))
fft2 = np.asarray(struct.unpack('>2048l',s.read('fft_data2',8192)))
ac0 = np.asarray(struct.unpack('>512q',s.read('ac_a0_real',4096)))
ac2 = np.asarray(struct.unpack('>512q',s.read('ac_a2_real',4096)))
cc02r = np.asarray(struct.unpack('>512q',s.read('cc_a0_a2_real',4096)))
cc02i = np.asarray(struct.unpack('>512q',s.read('cc_a0_a2_imag',4096)))

#--------------------------------------------------------------------------------------------------------------------------------------
#Fft Data Antenna 0
fft0l = list(fft0)
fd0 = splicing(fft0l)
magfd0 = abs(fd0)
phasefd0 = np.angle(fd0)*180/np.pi
#Fft Data Antenna 2
fft2l = list(fft2)
fd2 = splicing(fft2l)
magfd2 = abs(fd2)
phasefd2 = np.angle(fd2)*180/np.pi

#--------------------------------------------------------------------------------------------------------------------------------------
#Autocorrelation of A
magac0 = abs(ac0)
phaseac0 = np.angle(ac0)*180/np.pi
#Autocorrelation of B
magac2 = abs(ac2)
phaseac2 = np.angle(ac2)*180/np.pi
#Cross Correlation of a and b
cc02rl = list(cc02r)
cc02il = list(cc02i)
cc02 = merge(cc02rl,cc02il)
magcc02 = abs(cc02)
phasecc02 = np.angle(cc02)*180/np.pi
#Correlation Coefficient
corrco02 = magcc02 / np.sqrt(magac0*magac2)

#--------------------------------------------------------------------------------------------------------------------------------------
print "Plotting Data"
#Plots of Data
#Fft Data plots
plt.figure(1)
plt.title('Fft Data')

plt.subplot(211)
plt.title('Fft of Antenna A')
plt.plot(f,magfd0,'c')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.subplot(212)
plt.plot(f,phasefd0,'c')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(2)
plt.subplot(211)
plt.title('Fft of Antenna B')
plt.plot(f,magfd2,'g')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.subplot(212)
plt.plot(f,phasefd2,'g')
plt.ylabel('Phase in Degrees')
plt.grid(True)

#Correlation Plots
plt.figure(3)
plt.title('Autocorrelation of Antenna 0')

plt.subplot(211)
plt.title('Magnitude Response of AC of 0')
plt.plot(f,magac0,'c')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.subplot(212)
plt.title('Phase Response of AC of 0')
plt.plot(f,phaseac0,'c')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(4)
plt.title('Autocorrelation of Antenna 2')

plt.subplot(211)
plt.title('Magnitude Response of AC of 2')
plt.plot(f,magac2,'g')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.subplot(212)
plt.title('Phase Response of AC of 2')
plt.plot(f,phaseac2,'g')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(5)
plt.title('Cross Correlation of Antennas 0 & 2')

plt.subplot(211)
plt.title('Magnitude Response of CC of 0 & 2')
plt.plot(f,magcc02,'r')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.subplot(212)
plt.title('Phase Response of CC of 0 & 2')
plt.plot(f,phasecc02,'r')
plt.ylabel('Phase in Degrees')
plt.grid(True)

#Correlation Coefficient Plot
plt.figure(6) 
plt.title('Correlation Coefficient of Antenna 0 & 2')
plt.plot(f,corrco02,'m')
plt.grid(True)
plt.show()
