#To store Python commands used during testing
#Clk Freq = 250 MHz, Input signal freq = 20 Mhz at 3.0 dBm
#Using 12-input SNAP Board w/ RaspberryPi 
#10 stage biplex fft
#4-tap 1024-point polyphase filter bank

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

#Autocorrelation of a
aca_data = s.read('ac_a',8192)
aca = struct.unpack('>1024q',aca_data)
aca = np.asarray(aca)
magaca = abs(aca)
phaseaca = np.angle(aca)

#Autocorrelation of b
acb_data = s.read('ac_b',8192)
acb = struct.unpack('>1024q',acb_data)
acb = np.asarrau(acb)
magacb = abs(acb)
phaseacb = np.angle(acb)

#Cross Correlation of a and b
ccre_data = s.read('cc_ab_real',4096)
ccim_data = s.read('cc_ab_imag',4096)
ccre = struct.unpack('>1024l',ccre_data)
ccim = struct.unpack('>1024l',ccim_data)
ccrel = list(ccre)
cciml = list(ccim)
cc = []
i = 0
while i < 1024:
	cc.append(ccrel[i]+cciml[i]*1j)
	i += 1

cc = np.asarray(cc)
magcc = abs(cc)
phasecc = np.angle(cc)

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


