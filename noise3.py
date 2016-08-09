#Clk Freq = 250 MHz, Input signal freq = 75 Mhz at -6.0 dBm
#Using 12-input SNAP Board w/ RaspberryPi 
#10 stage fft_biplex_real_2x
#4-tap 1024-point polyphase filter bank
#This one will Correlate all 12 inputs at the same time
#2 input worked (noise3_2016-8-9-1406.bof)
#Currently testing 4 input 1 ADC (noise3_2016-8-9-1501.bof)

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
fn = np.linspace(0,511,512)
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
#Extra accumulations done before reading data from BRAMs for saftey of data
#It tosses out unknown initial state junk values that would mess up data.
#Should be working by final accumulation transition to read BRAMs
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
ac0 = np.asarray(struct.unpack('>512q',s.read('ac_a0_real',4096)))
ac1 = np.asarray(struct.unpack('>512q',s.read('ac_a1_real',4096)))
ac2 = np.asarray(struct.unpack('>512q',s.read('ac_a2_real',4096)))
ac3 = np.asarray(struct.unpack('>512q',s.read('ac_a3_real',4096)))
cc01r = np.asarray(struct.unpack('>512q',s.read('cc_a0_a1_real',4096)))
cc01i = np.asarray(struct.unpack('>512q',s.read('cc_a0_a1_imag',4096)))
cc02r = np.asarray(struct.unpack('>512q',s.read('cc_a0_a2_real',4096)))
cc02i = np.asarray(struct.unpack('>512q',s.read('cc_a0_a2_imag',4096)))
cc03r = np.asarray(struct.unpack('>512q',s.read('cc_a0_a3_real',4096)))
cc03i = np.asarray(struct.unpack('>512q',s.read('cc_a0_a3_imag',4096)))
cc12r = np.asarray(struct.unpack('>512q',s.read('cc_a1_a2_real',4096)))
cc12i = np.asarray(struct.unpack('>512q',s.read('cc_a1_a2_imag',4096)))
cc13r = np.asarray(struct.unpack('>512q',s.read('cc_a1_a3_real',4096)))
cc13i = np.asarray(struct.unpack('>512q',s.read('cc_a1_a3_imag',4096)))
cc23r = np.asarray(struct.unpack('>512q',s.read('cc_a2_a3_real',4096)))
cc23i = np.asarray(struct.unpack('>512q',s.read('cc_a2_a3_imag',4096)))

#--------------------------------------------------------------------------------------------------------------------------------------
#Autocorrelation of 0
magac0 = abs(ac0)
phaseac0 = np.angle(ac0)*180/np.pi
#Autocorrelation of 1
magac1 = abs(ac1)
phaseac1 = np.angle(ac1)*180/np.pi
#Autocorrelation of 2
magac2 = abs(ac2)
phaseac2 = np.angle(ac2)*180/np.pi
#Autocorrelation of 3
magac3 = abs(ac3)
phaseac3 = np.angle(ac3)*180/np.pi

#--------------------------------------------------------------------------------------------------------------------------------------
#Cross Correlation of 0 and 1
cc01rl = list(cc01r)
cc01il = list(cc01i)
cc01 = merge(cc01rl,cc01il)
magcc01 = abs(cc01)
phasecc01 = np.angle(cc01)*180/np.pi
#Cross Correlation of 0 and 2
cc02rl = list(cc02r)
cc02il = list(cc02i)
cc02 = merge(cc02rl,cc02il)
magcc02 = abs(cc02)
phasecc02 = np.angle(cc02)*180/np.pi
#Cross Correlation of 0 and 3
cc03rl = list(cc03r)
cc03il = list(cc03i)
cc03 = merge(cc03rl,cc03il)
magcc03 = abs(cc03)
phasecc03 = np.angle(cc03)*180/np.pi
#Cross Correlation of 1 and 2
cc12rl = list(cc12r)
cc12il = list(cc12i)
cc12 = merge(cc12rl,cc12il)
magcc12 = abs(cc12)
phasecc12 = np.angle(cc12)*180/np.pi
#Cross Correlation of 1 and 3
cc13rl = list(cc13r)
cc13il = list(cc13i)
cc13 = merge(cc13rl,cc13il)
magcc13 = abs(cc13)
phasecc13 = np.angle(cc13)*180/np.pi
#Cross Correlation of 2 and 3
cc23rl = list(cc23r)
cc23il = list(cc23i)
cc23 = merge(cc23rl,cc23il)
magcc23 = abs(cc23)
phasecc23 = np.angle(cc23)*180/np.pi

#--------------------------------------------------------------------------------------------------------------------------------------
print "Plotting Data"
#Autocorrelation Plots
plt.figure(1)
plt.title('Autocorrelation of Antenna 0')
plt.subplot(211)
plt.title('Magnitude Response of AC of 0')
plt.plot(fn,magac0,'g')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of AC of 0')
plt.plot(fn,phaseac0,'g')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(2)
plt.title('Autocorrelation of Antenna 1')
plt.subplot(211)
plt.title('Magnitude Response of AC of 1')
plt.plot(fn,magac1,'r')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of AC of 1')
plt.plot(fn,phaseac1,'r')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(3)
plt.title('Autocorrelation of Antenna 2')
plt.subplot(211)
plt.title('Magnitude Response of AC of 2')
plt.plot(fn,magac2,'c')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of AC of 2')
plt.plot(fn,phaseac2,'c')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(4)
plt.title('Autocorrelation of Antenna 3')
plt.subplot(211)
plt.title('Magnitude Response of AC of 3')
plt.plot(fn,magac3,'y')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of AC of 3')
plt.plot(fn,phaseac3,'y')
plt.ylabel('Phase in Degrees')
plt.grid(True)

#--------------------------------------------------------------------------------------------------------------------------------------
#Cross Correlation Plots

plt.figure(5)
plt.title('Cross Correlation of Antennas 0 & 1')
plt.subplot(211)
plt.title('Magnitude Response of CC of 0 & 1')
plt.plot(fn,magcc01,'k')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 0 & 1')
plt.plot(fn,phasecc01,'k')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(6)
plt.title('Cross Correlation of Antennas 0 & 2')
plt.subplot(211)
plt.title('Magnitude Response of CC of 0 & 2')
plt.plot(fn,magcc02,'m')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 0 & 2')
plt.plot(fn,phasecc02,'m')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(7)
plt.title('Cross Correlation of Antennas 0 & 3')
plt.subplot(211)
plt.title('Magnitude Response of CC of 0 & 3')
plt.plot(fn,magcc03,'k')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 0 & 3')
plt.plot(fn,phasecc03,'k')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(8)
plt.title('Cross Correlation of Antennas 1 & 2')
plt.subplot(211)
plt.title('Magnitude Response of CC of 1 & 2')
plt.plot(fn,magcc12,'k')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 1 & 2')
plt.plot(fn,phasecc12,'k')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(9)
plt.title('Cross Correlation of Antennas 1 & 3')
plt.subplot(211)
plt.title('Magnitude Response of CC of 1 & 3')
plt.plot(fn,magcc13,'m')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 1 & 3')
plt.plot(fn,phasecc13,'m')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(10)
plt.title('Cross Correlation of Antennas 2 & 3')
plt.subplot(211)
plt.title('Magnitude Response of CC of 2 & 3')
plt.plot(fn,magcc23,'k')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 2 & 3')
plt.plot(fn,phasecc23,'k')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.show()
