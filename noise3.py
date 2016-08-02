#Clk Freq = 250 MHz, Input signal freq = 75 Mhz at 0.0 dBm
#Using 12-input SNAP Board w/ RaspberryPi 
#10 stage biplex fft
#4-tap 1024-point polyphase filter bank
#ADC stats added, host selection added

import corr, struct, numpy as np, matplotlib.pyplot as plt, time

#--------------------------------------------------------------------------------------------------------------------------------------
from argparse import ArgumentParser
p = ArgumentParser(description = 'python noise2.py [options] ')
p.add_argument('host', type = str, default = '10.0.1.217', help = 'Specify the host name')
p.add_argument('-s', '--shift', dest = 'shift', type = int, default = 2047, help = 'set shift value for fft biplex block')
p.add_argument('-a', '--anta', dest = 'anta', type = int, default = 0, help = 'set first antenna to be correlated')
p.add_argument('-b', '--antb', dest = 'antb', type = int, default = 4, help = 'set second antenna to be correlated')
p.add_argument('-l', '--length', dest = 'length', type = int, default = 2e6, help = 'set # of spectra to be accumulated')

args = p.parse_args()
host = args.host
shift = args.shift
anta = args.anta
antb = args.antb
length = args.length 

#--------------------------------------------------------------------------------------------------------------------------------------
#Merges real and imaginary parts of fft data into a single number
def splicing(x):
	temp = []
	z = 0
	while z < 2048:
		temp.append(x[z+1] + x[z]*1j)
		z += 2
	return np.asarray(temp)

#Controls number of accumulations with n
def accumulation(n):
	k = 0
	while k < n:
		p = 0
		s.write_int('trig',0)
		s.write_int('trig',1)
		s.write_int('trig',0)
		if k == n/4:
			print "Quarter way"
		elif k == n/2:
			print "Half way"
		elif k == n*3/4:
			print "3/4 of the way"
		while p < 8192:
			p += 1
		k += 1


#Merges real and imaginary parts of Correlation data into a single number
def merge(x,y):
	temp = []
	w = 0
	while w < 1024:
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
#Antenna Selection
print "Selecting Antennas"
s.write_int('antenna_a',anta)
s.write_int('antenna_b',antb)
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


#--------------------------------------------------------------------------------------------------------------------------------------
overflow = s.read_int('overflow')
print overflow

#--------------------------------------------------------------------------------------------------------------------------------------
print "Reading Adc Data"
#Adc Data Antenna A
ad1 = np.asarray(struct.unpack('>65536b',s.read('adc_data1',65536)))
sigma1 = np.sqrt(np.var(ad1))
print "Hey this one is sigma antenna 1"
print sigma1
rms1 = np.sqrt(np.mean(np.square(ad1)))
print "Hey this one is rms antenna 1"
print rms1

#Adc Data Antenna B
ad2 = np.asarray(struct.unpack('>65536b',s.read('adc_data2',65536)))
print "Done"
sigma2 = np.sqrt(np.var(ad2))
print "Hey this one is sigma antenna 2"
print sigma2
rms2 = np.sqrt(np.mean(np.square(ad2)))
print "Hey this one is rms antenna 2"
print rms2

#--------------------------------------------------------------------------------------------------------------------------------------
print "Reading Fft Data"
#Fft Data Antenna A
fft1 = np.asarray(struct.unpack('>2048l',s.read('fft_data1',8192)))
fft1l = list(fft1)
fd1 = splicing(fft1l)
magfd1 = abs(fd1)
phasefd1 = np.angle(fd1)*180/np.pi

#Fft Data Antenna B
fft2 = np.asarray(struct.unpack('>2048l',s.read('fft_data2',8192)))
fft2l = list(fft2)
fd2 = splicing(fft2l)
magfd2 = abs(fd2)
phasefd2 = np.angle(fd2)*180/np.pi
print "Done"

#--------------------------------------------------------------------------------------------------------------------------------------
print "Reading Correlation Data"
#Autocorrelation of A
acar = np.asarray(struct.unpack('>1024q',s.read('ac_a_real',8192)))
acai = np.asarray(struct.unpack('>1024q',s.read('ac_a_imag',8192)))
acarl = list(acar)
acail = list(acai)
aca = merge(acarl,acail)
magaca = abs(aca)
phaseaca = np.angle(aca)*180/np.pi

#Autocorrelation of B
acbr = np.asarray(struct.unpack('>1024q',s.read('ac_b_real',8192)))
acbi = np.asarray(struct.unpack('>1024q',s.read('ac_b_imag',8192)))
acbrl = list(acbr)
acbil = list(acbi)
acb = merge(acbrl,acbil)
magacb = abs(acb)
phaseacb = np.angle(acb)*180/np.pi

#Cross Correlation of a and b
ccabr = np.asarray(struct.unpack('>1024q',s.read('cc_ab_real',8192)))
ccabi = np.asarray(struct.unpack('>1024q',s.read('cc_ab_imag',8192)))
ccabrl = list(ccabr)
ccabil = list(ccabi)
cc = merge(ccabrl,ccabil)
magcc = abs(cc)
phasecc = np.angle(cc)*180/np.pi
print cc[0]
print cc[511]
print cc[1023]
print "Done"

#--------------------------------------------------------------------------------------------------------------------------------------
print "Plotting Data"
#Plots of Data
#Fft Data plots
plt.figure(1)
plt.title('Fft Data')

plt.subplot(211)
plt.title('Fft of Antenna A')
plt.plot(f,magfd1,'c')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.subplot(212)
plt.plot(f,phasefd1,'c')
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
plt.title('Autocorrelation of Antenna A')

plt.subplot(211)
plt.title('Magnitude Response of AC of A')
plt.plot(f,magaca,'c')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.subplot(212)
plt.title('Phase Response of AC of A')
plt.plot(f,phaseaca,'c')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(4)
plt.title('Autocorrelation of Antenna B')

plt.subplot(211)
plt.title('Magnitude Response of AC of B')
plt.plot(f,magacb,'g')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.subplot(212)
plt.title('Phase Response of AC of B')
plt.plot(f,phaseacb,'g')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(5)
plt.title('Cross Correlation of Antennas A & B')

plt.subplot(211)
plt.title('Magnitude Response of CC of A & B')
plt.plot(f,magcc,'r')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.subplot(212)
plt.title('Phase Response of CC of A & B')
plt.plot(f,phasecc,'r')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(6)
plt.title('Adc Data Antenna 1')
plt.plot(t,ad1,'c-')
plt.axis([0,65536,-136,135])
plt.grid(True)

plt.figure(7)
plt.hist(ad1, bins=256) 
plt.title("Histogram of Antenna 1")

plt.figure(8)
plt.title('Adc Data Antenna 2')
plt.plot(t,ad2, 'g-')
plt.axis([0,65536,-136,135])
plt.grid(True)

plt.figure(9)
plt.hist(ad2, bins=256) 
plt.title("Histogram of Antenna 2")
plt.show()
