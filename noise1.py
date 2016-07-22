#To store Python commands used during testing
#Clk Freq = 250 MHz, Input signal freq = 20 Mhz at 3.0 dBm
#Using 12-input SNAP Board w/ RaspberryPi 
#10 stage biplex fft
#8-tap 1024-point polyphase filter bank

import corr, struct, numpy as np, matplotlib.pyplot as plt
s = corr.katcp_wrapper.FpgaClient('10.0.1.217')

s.write_int('shift',2047)
#Antenna Selection
s.write_int('antenna_a',0)
s.write_int('antenna_b',4)

f = np.linspace(0,1023,1024)
accumulation(10000)

#Adc Data Antenna A
ad1 = np.asarray(struct.unpack('>1024b',s.read('adc_data1',1024)))
#Adc Data Antenna B
ad2 = np.asarray(struct.unpack('>1024b',s.read('adc_data2',1024)))

#Fft Data Antenna A
fft1 = np.asarray(struct.unpack('>2048l',s.read('fft_data1',8192)))
fft1l = list(fft1)
fd1 = np.asarray(splicing(fftl1))
magfd1 = abs(fd1)
phasefd1 = np.angle(fd1)*180/np.pi
#Fft Data Antenna B
fft2 = np.asarray(struct.unpack('>2048l',s.read('fft_data2',8192)))
fft2l = list(fft2)
fd2 = np.asarray(splicing(fftl2))
magfd2 = abs(fd2)
phasefd2 = np.angle(fd2)*180/np.pi

#Autocorrelation of A
aca = np.asarray(struct.unpack('>2048q',s.read('ac_a',16384)))
acal = list(aca)
aca = np.asarray(splicing(acal))
magaca = abs(aca)
phaseaca = np.angle(aca)*180/np.pi

#Autocorrelation of B
acb = np.asarray(struct.unpack('>2048q',s.read('ac_b',16384)))
acbl = list(ccab)
acb = np.asarray(splicing(acbl))
magacb = abs(acb)
phaseacb = np.angle(acb)*180/np.pi

#Cross Correlation of a and b
ccab = np.asarray(struct.unpack('>2048q',s.read('cc_ab',16384)))
ccabl = list(ccab)
cc = np.asarray(splicing(ccabl))
magcc = abs(cc)
phasecc = np.angle(cc)*180/np.pi

#Plots of Data
#Adc Plot
plt.figure(1)
plt.title('Adc Data')

plt.subplot(211)
plt.title('Antenna A')
plt.plot(f,ad1,'k')

plt.subplot(212)
plt.title('Antenna B')
plt.plot(f,ad2,'k')
plt.show()

#Fft Data plots
plt.figure(2)
plt.title('Fft Data')

plt.subplot(411)
plt.title('Fft of Antenna A')
plt.plot(f,magfd1,'k')
plt.subplot(412)
plt.plot(f,phasefd1,'k')

plt.subplot(413)
plt.title('Fft of Antenna B')
plt.plot(f,magfd2,'k')
plt.subplot(414)
plt.plot(f,phasefd2,'k')
plt.show()

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
plt.show()

plt.figure(4)
plt.title('Autocorrelation of Antenna B')

plt.subplot(211)
plt.title('Magnitude Response of AC of B')
plt.plot(f,magacb,'m')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.subplot(212)
plt.title('Phase Response of AC of B')
plt.plot(f,phaseacb,'m')
plt.ylabel('Phase in Degrees')
plt.grid(True)
plt.show()

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

#Merges real and imaginary parts of data into a single number
def splicing(x):
	temp = []
	i = 0
	while i < 2048:
		temp.append(x[i] + x[i+1]*1j)
		i += 2
	return temp

#Controls number of accumulations with n
def accumulation(n):
	k = 0
	while k < n:
		p = 0
		s.write_int('trig',0)
		s.write_int('trig',1)
		s.write_int('trig',0)
		while p < 5000:
			p += 1
		k += 1
