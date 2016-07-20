#To store Python commands used during testing
#Clk Freq = 250 MHz, Input signal freq = 20 Mhz at 3.0 dBm
#Using 12-input SNAP Board w/ RaspberryPi 
#10 stage biplex fft
#8-tap 1024-point polyphase filter bank

import corr, struct, numpy as np, matplotlib.pyplot as plt
s = corr.katcp_wrapper.FpgaClient('10.0.1.217')

s.write_int('shift',2047)
s.write_int('antenna_a',0)
s.write_int('antenna_b',1)

s.write_int('trig',0)
s.write_int('trig',1)
s.write_int('trig',0)

s.read_int('overflow')
s.read_int('address_ac_a')
s.read_int('address_ac_b')
s.read_int('address_cc_re')
s.read_int('address_cc_im')
s.read_int('address_fft_a')
s.read_int('address_fft_b')

f = np.linspace(0,1023,1024)

k = 0 
p = 0

#Controls number of accumulations with k
while k < 2000:
	p = 0
	s.write_int('trig',0)
	s.write_int('trig',1)
	s.write_int('trig',0)
	while p < 10000:
		p += 1
	k += 1

#Cross Correlation of a and b
ccab = struct.unpack('>2048q',s.read('cc_ab',16384))
ccab = np.asarray(ccab)
ccabl = list(ccab)
temp = []
i = 0
while i < 2048:
	temp.append(ccabl[i] + ccabl[i+1]*1j)
	i += 2
	
cc = np.asarray(temp)
magcc = abs(cc)
phasecc = np.angle(cc)

#Autocorrelation of A
aca = struct.unpack('>2048q',s.read('ac_a',16384))
aca = np.asarray(aca)
acal = list(aca)
temp = []
i = 0
while i < 2048:
	temp.append(acal[i] + acal[i+1]*1j)
	i += 2
	
aca = np.asarray(temp)
magaca = abs(aca)
phaseaca = np.angle(aca)

#Autocorrelation of B
acb = struct.unpack('>2048q',s.read('ac_b',16384))
acb = np.asarray(ccab)
acbl = list(ccab)
temp = []
i = 0
while i < 2048:
	temp.append(acbl[i] + acbl[i+1]*1j)
	i += 2
	
acb = np.asarray(temp)
magacb = abs(acb)
phaseacb = np.angle(acb)


plt.figure(1)
plt.title('Autocorrelation of Antenna A')

plt.subplot(211)
plt.title('Magnitude Response of AC of A')
plt.plot(f,magaca,'b')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.subplot(212)
plt.title('Phase Response of AC of A')
plt.plot(f,phaseaca*180/np.pi,'b')
plt.ylabel('Phase in Degrees')
plt.grid(True)
plt.show()

plt.figure(2)
plt.title('Autocorrelation of Antenna B')

plt.subplot(211)
plt.title('Magnitude Response of AC of B')
plt.plot(f,magacb,'g')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.subplot(212)
plt.title('Phase Response of AC of B')
plt.plot(f,phaseacb*180/np.pi,'g')
plt.ylabel('Phase in Degrees')
plt.grid(True)
plt.show()

plt.figure(3)
plt.title('Cross Correlation of Antennas A & B')

plt.subplot(211)
plt.title('Magnitude Response of CC of A & B')
plt.plot(f,magcc,'r')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.subplot(212)
plt.title('Phase Response of CC of A & B')
plt.plot(f,phasecc*180/np.pi,'r')
plt.ylabel('Phase in Degrees')
plt.grid(True)
plt.show()


