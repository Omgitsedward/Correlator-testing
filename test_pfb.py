#To store Python commands used during testing
#Clk Freq = 250 MHz, Input signal freq = 20 Mhz at 3.0 dBm
#Using 12-input SNAP Board w/ RaspberryPi 
#10 stage biplex fft
#4-tap 1024-point polyphase filter bank

import corr, struct, numpy as np, matplotlib.pyplot as plt
s = corr.katcp_wrapper.FpgaClient('10.0.1.217')

s.is_connected()
s.est_brd_clk()

s.write_int('shift',2047)
s.write_int('trig',0)
s.write_int('trig',1)
s.write_int('trig',0)

s.read_int('address_fft')
s.read_int('overflow')

f = np.linspace(0,1023,1024)
fft_data = s.read('fft_data',8192)

fd = struct.unpack('>2048l',fft_data)
fd = np.asarray(fd)
fdl = list(fd)
temp = []
i = 0
while i < 2048:
	temp.append(fdl[i]+fdl[i+1]*1j)
	i += 2
	
temp = np.asarray(temp)
magtemp = abs(temp)
phasetemp = np.angle(temp)

plt.figure(2)

plt.subplot(211)
plt.title('Magnitude Response of Filtered Fft data')
plt.plot(f,magtemp,'r')
plt.grid(True)

plt.subplot(212)
plt.title('Phase Response of Filtered Fft data')
plt.plot(f,phasetemp,'r')
plt.grid(True)
plt.show()
