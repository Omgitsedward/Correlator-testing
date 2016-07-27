
import corr, struct, numpy as np, matplotlib.pyplot as plt, time
s = corr.katcp_wrapper.FpgaClient('10.0.1.217',7147,timeout = 10)

s.write_int('cnt_rst',0)
s.write_int('cnt_rst',1)
s.write_int('cnt_rst',0)

s.read_int('address_adc')

adc_data = s.read('adc_data',1024)
ad = struct.unpack('>1024b',adc_data)
ad = np.asarray(ad)
time = np.linspace(0,1023,1024)

sigma = np.sqrt(np.var(ad))
print "Hey this one is sigma"
print sigma

rms = np.sqrt(np.mean(np.square(ad)))
print "Hey this one is rms"
print rms

plt.figure(1)
plt.title('adc data')
plt.plot(time,ad,'k')
plt.grid(True)

plt.figure(2)
plt.hist(ad, bins=256) 
plt.title("Histogram with 'auto' bins")
plt.show()
