#To store Python commands used during testing
#Clk Freq = 250 MHz, Input signal freq = 20 Mhz at 3.0 dBm
#Using 12-input SNAP Board w/ RaspberryPi 
#10 stage biplex fft
#8-tap 1024-point polyphase filter bank
#Add Host selection
import corr, struct, numpy as np, matplotlib.pyplot as plt, time

from argparse import ArgumentParser
p = ArgumentParser(description = 'python noise1.py [options] ')
p.add_argument('-s', '--shift', dest = 'shift', type = int, default = 2047, help = 'set shift value for fft biplex block')
p.add_argument('-a', '--anta', dest = 'anta', type = int, default = 0, help = 'set first antenna to be correlated')
p.add_argument('-b', '--antb', dest = 'antb', type = int, default = 4, help = 'set second antenna to be correlated')
p.add_argument('-i', '--iteration', dest = 'iteration', type = int, default = 1000, help = 'set accumulation number')

args = p.parse_args()
shift = args.shift
anta = args.anta
antb = args.antb
iteration = args.iteration 

#Merges real and imaginary parts of fft data into a single number
def splicing(x):
	temp = []
	z = 0
	while z < 2048:
		temp.append(x[z] + x[z+1]*1j)
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
		if k == n/2:
			print "Halfway"
		while p < 8197:
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

print "Connecting to Fpga"
s = corr.katcp_wrapper.FpgaClient('10.0.1.217',7147,timeout = 10)
time.sleep(1)
if s.is_connected():
	print "Connected"
else:
	print "Not connected"
	
f = np.linspace(0,1023,1024)
print "Setting Shift value"
s.write_int('shift',shift)
print "Done"

#Antenna Selection
print "Selecting Antennas"
s.write_int('antenna_a',anta)
s.write_int('antenna_b',antb)
print "Done"

print "Starting accumulation process"
accumulation(iteration)
print "Done"

if s.read_int('overflow') != 0:
	print "Overflow"

print "Reading Adc Data"
#Adc Data Antenna A
ad1 = np.asarray(struct.unpack('>1024b',s.read('adc_data1',1024)))

#Adc Data Antenna B
ad2 = np.asarray(struct.unpack('>1024b',s.read('adc_data2',1024)))
print "Done"

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
print "Done"

print "Plotting Data"
#Plots of Data
#Adc Plot
plt.figure(1)
plt.title('Adc Data')

plt.subplot(211)
plt.title('Antenna A')
plt.plot(f,ad1,'c')
plt.grid(True)

plt.subplot(212)
plt.title('Antenna B')
plt.plot(f,ad2,'g')
plt.grid(True)

#Fft Data plots
plt.figure(2)
plt.title('Fft Data')

plt.subplot(411)
plt.title('Fft of Antenna A')
plt.plot(f,magfd1,'c')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.subplot(412)
plt.plot(f,phasefd1,'c')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.subplot(413)
plt.title('Fft of Antenna B')
plt.plot(f,magfd2,'g')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.subplot(414)
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
plt.show()
