
import corr, struct, numpy as np, matplotlib.pyplot as plt, time
s = corr.katcp_wrapper.FpgaClient('10.0.1.217',7147,timeout = 10)
time.sleep(1)

s.write_int('cnt_rst',0)
s.write_int('cnt_rst',1)
s.write_int('cnt_rst',0)

print s.read_int('address')

adc_data = s.read('adc_data',65536)
ad = struct.unpack('>65536b',adc_data)
ad = np.asarray(ad)
time = np.linspace(0,65535,65536)

sigma = np.sqrt(np.var(ad))
print "Hey this one is sigma"
print sigma

rms = np.sqrt(np.mean(np.square(ad)))
print "Hey this one is rms"
print rms

plt.figure(1)
plt.title('adc data')
plt.plot(time,ad,'ko')
plt.axis([0,65536,-136,135])
plt.grid(True)

plt.figure(2)
plt.hist(ad, bins=256) 
plt.title("Histogram with 256 bins")
plt.show()
