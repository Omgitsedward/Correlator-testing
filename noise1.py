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

#Merges real and imaginary parts of data into a single number
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
		while p < 8192:
			p += 1
		k += 1

print "Connecting to Fpga"
s = corr.katcp_wrapper.FpgaClient('10.0.1.217',7147,timeout = 10)
time.sleep(1)
if s.is_connected():
	print "Connected"
else:
	print "not connecting"
	
f = np.linspace(0,1023,1024)
print "Setting Shift value"
s.write_int('shift',shift)

#Antenna Selection
print "Selecting Antennas"
s.write_int('antenna_a',anta)
s.write_int('antenna_b',antb)
print "Starting accumulation process"
accumulation(iteration)

print "Reading Adc Data"
#Adc Data Antenna A
ad1 = np.asarray(struct.unpack('>1024b',s.read('adc_data1',1024)))

#Adc Data Antenna B
ad2 = np.asarray(struct.unpack('>1024b',s.read('adc_data2',1024)))

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

print "Reading Correlation Data"
#Autocorrelation of A
aca = np.asarray(struct.unpack('>2048q',s.read('ac_a',16384)))
acal = list(aca)
aca = splicing(acal)
magaca = abs(aca)
phaseaca = np.angle(aca)*180/np.pi

#Autocorrelation of B
acb = np.asarray(struct.unpack('>2048q',s.read('ac_b',16384)))
acbl = list(acb)
acb = splicing(acbl)
magacb = abs(acb)
phaseacb = np.angle(acb)*180/np.pi

#Cross Correlation of a and b
ccab = np.asarray(struct.unpack('>2048q',s.read('cc_ab',16384)))
ccabl = list(ccab)
cc = splicing(ccabl)
magcc = abs(cc)
phasecc = np.angle(cc)*180/np.pi

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
