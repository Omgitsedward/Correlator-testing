#to store commands during ipython testing
#Clk freq = 250 MHz, Input signal = 20 MHz
#Using 12-input SNAP Board w/ RaspberryPi 

import corr, struct, numpy as np, matplotlib.pyplot as plt
s = corr.katcp_wrapper.FpgaClient('10.0.1.217')

s.write_int('shift',0)
s.write_int('trig',0)
s.write_int('trig',1)
s.write_int('trig',0)

s.read_int('overflow')
s.read_int('address_fft')
s.read_int('address_adc')

adc_data = s.read('adc_data',1024)
ad = struct.unpack('>1024b',adc_data)
ad = np.asarray(ad)

adcfft = np.fft.fft(ad)
magaf = abs(ad)
phaseaf = np.angle(ad)

fft_data = s.read('fft_data',8192)
fd = struct.unpack('>2048l',fft_data)
fd = np.asarray(fd)
fdl = list(fd)
temp = []
i = 0

while i < 1024:
	temp.append(fdl[i]+fdl[i+1]*1j)
	i += 2

temp = np.asarray(temp)
magtemp = abs(temp)
phasetemp = np.angle(temp)

f = np.linspace(0,1023,1024)
time = np.linspace(4e-9,4.096e-6,1024)

plt.figure(1)

plt.subplot(511)
plt.title('adc data')
plt.plot(time,ad,'k')
plt.grid(True)

plt.subplot(512)
plt.title('Magnitude Response of fft adc data')
plt.plot(f,magaf,'b')
plt.grid(True)

plt.subplot(513)
plt.title('Phase Response of fft adc data')
plt.plot(f,phaseaf,'b')
plt.grid(True)

plt.subplot(514)
plt.title('Magnitude Response of fft biplex block')
plt.plot(f,magtemp,'g')
plt.grid(True)

plt.subplot(515)
plt.title('Phase Response of fft biplex block')
plt.plot(f,phasetemp,'g')
plt.grid(True)
plt.show()



