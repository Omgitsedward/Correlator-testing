#Eddie Toral
#CAMPARE 2016 Summer Research Undergrad
#August 15th 2016
#12-input Correlator for SNAP Board
#
#	Testing info:
#		Clk Freq = 250 MHz, Input signal freq = 75 Mhz at -6.0 dBm 
#	Noise sources: 
#		Amps in series for one source, L-band generator for the other. 
#		Couplers used in reverse to combine tone with noise to use for testing.
#
#	Using 12-input SNAP Board w/ RaspberryPi 
#	10 stage fft_biplex_real_2x
#	4-tap 1024 polyphase filter bank
#	Model & code will Correlate all 12 inputs at the same time
#
#	2 input worked (noise3_2016-8-9_1406.bof)
#	4 input 1 ADC worked (noise3_2016-8-9_1501.bof)
#	12 input, 3 ADC works (noise3_2016-8-14_.bof)

import corr, struct, numpy as np, matplotlib.pyplot as plt, time

#--------------------------------------------------------------------------------------------------------------------------------------
from argparse import ArgumentParser
p = ArgumentParser(description = 'python noise3.py [options] ')
p.add_argument('host', type = str, default = '10.0.1.217', help = 'Specify the host name')
p.add_argument('-s', '--shift', dest = 'shift', type = int, default = 2047, help = 'set shift value for fft biplex block')
p.add_argument('-l', '--length', dest = 'length', type = int, default = 2e6, help = 'set # of spectra to be accumulated')

args = p.parse_args()
host = args.host
shift = args.shift
length = args.length 

#--------------------------------------------------------------------------------------------------------------------------------------
#Merges real and imaginary parts of Cross Correlation data into a single number
def merge(x,y):
	temp = []
	w = 0
	while w < 512:
		temp.append(x[w] + y[w]*1j)
		w += 1
	return np.asarray(temp)
	
#--------------------------------------------------------------------------------------------------------------------------------------
print "Connecting to Fpga"
s = corr.katcp_wrapper.FpgaClient(host,7147,timeout = 10)
time.sleep(1)

#--------------------------------------------------------------------------------------------------------------------------------------
#To make sure RaspberryPi and SNAP Board are connected
if s.is_connected():
	print "Connected"
else:
	print "Not connected"

#--------------------------------------------------------------------------------------------------------------------------------------
#To be used for plotting purposes at the end of the code
fn = np.linspace(0,511,512)

#--------------------------------------------------------------------------------------------------------------------------------------
#Setting FFT Biplex x2 Shift value
print "Setting Shift value"
s.write_int('shift',shift)
print "Done"

#--------------------------------------------------------------------------------------------------------------------------------------
#Setting the Accumulation length to option choice selected
print "Starting accumulation process"
s.write_int('acc_len',length)

#--------------------------------------------------------------------------------------------------------------------------------------
#Start Data Processing & Capture
#Sending Sync Pulse
s.write_int('trig',0)
s.write_int('trig',1)
s.write_int('trig',0)

#Extra accumulations done before reading data from BRAMs for saftey of data
#It tosses out unknown initial state junk values that would mess up data.
#Should be working by final accumulation transition to read BRAMs
#Dont freakout if the numbers are big or negative, only thing that matters is that acc_num goes up by 1 each time it's printed.
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
print "Done"

#--------------------------------------------------------------------------------------------------------------------------------------
#If FFT Biplex block overflows, the output here would be 1
overflow = s.read_int('overflow')
print overflow

#--------------------------------------------------------------------------------------------------------------------------------------
#Reading Data from all Correlation BRAM Blocks
#Antenna names correspond to the antenna names for the inputs on the SNAP board.
#		ie. ADC0 Board input -> ac0,a0, etc. in the following lines
#Cross Correlations will have the naming convention of ccantenna_Aantenna_B
#		ie. Cross correlation of ADC0 and ADC3 board inputs will be named cc03, etc.

#Autocorrelation Data
ac0 = np.asarray(struct.unpack('>512l',s.read('ac_a0_real',2048)))
ac1 = np.asarray(struct.unpack('>512l',s.read('ac_a1_real',2048)))
ac2 = np.asarray(struct.unpack('>512l',s.read('ac_a2_real',2048)))
ac3 = np.asarray(struct.unpack('>512l',s.read('ac_a3_real',2048)))
ac4 = np.asarray(struct.unpack('>512l',s.read('ac_a4_real',2048)))
ac5 = np.asarray(struct.unpack('>512l',s.read('ac_a5_real',2048)))
ac6 = np.asarray(struct.unpack('>512l',s.read('ac_a6_real',2048)))
ac7 = np.asarray(struct.unpack('>512l',s.read('ac_a7_real',2048)))
ac8 = np.asarray(struct.unpack('>512l',s.read('ac_a8_real',2048)))
ac9 = np.asarray(struct.unpack('>512l',s.read('ac_a9_real',2048)))
ac10 = np.asarray(struct.unpack('>512l',s.read('ac_a10_real',2048)))
ac11 = np.asarray(struct.unpack('>512l',s.read('ac_a11_real',2048)))

#Cross Correlation Data
#Antenna 0 Cross 1 - 11
cc01r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a1_real',2048)))
cc01i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a1_imag',2048)))
cc02r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a2_real',2048)))
cc02i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a2_imag',2048)))
cc03r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a3_real',2048)))
cc03i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a3_imag',2048)))
cc04r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a4_real',2048)))
cc04i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a4_imag',2048)))
cc05r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a5_real',2048)))
cc05i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a5_imag',2048)))
cc06r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a6_real',2048)))
cc06i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a6_imag',2048)))
cc07r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a7_real',2048)))
cc07i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a7_imag',2048)))
cc08r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a8_real',2048)))
cc08i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a8_imag',2048)))
cc09r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a9_real',2048)))
cc09i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a9_imag',2048)))
cc010r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a10_real',2048)))
cc010i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a10_imag',2048)))
cc011r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a11_real',2048)))
cc011i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a11_imag',2048)))

#Antenna 1 Cross 2 - 11
cc12r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a2_real',2048)))
cc12i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a2_imag',2048)))
cc13r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a3_real',2048)))
cc13i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a3_imag',2048)))
cc14r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a4_real',2048)))
cc14i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a4_imag',2048)))
cc15r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a5_real',2048)))
cc15i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a5_imag',2048)))
cc16r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a6_real',2048)))
cc16i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a6_imag',2048)))
cc17r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a7_real',2048)))
cc17i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a7_imag',2048)))
cc18r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a8_real',2048)))
cc18i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a8_imag',2048)))
cc19r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a9_real',2048)))
cc19i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a9_imag',2048)))
cc110r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a10_real',2048)))
cc110i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a10_imag',2048)))
cc111r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a11_real',2048)))
cc111i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a11_imag',2048)))

#Atenna 2 Cross 3 - 11
cc23r = np.asarray(struct.unpack('>512l',s.read('cc_a2_a3_real',2048)))
cc23i = np.asarray(struct.unpack('>512l',s.read('cc_a2_a3_imag',2048)))
cc24r = np.asarray(struct.unpack('>512l',s.read('cc_a2_a4_real',2048)))
cc24i = np.asarray(struct.unpack('>512l',s.read('cc_a2_a4_imag',2048)))
cc25r = np.asarray(struct.unpack('>512l',s.read('cc_a2_a5_real',2048)))
cc25i = np.asarray(struct.unpack('>512l',s.read('cc_a2_a5_imag',2048)))
cc26r = np.asarray(struct.unpack('>512l',s.read('cc_a2_a6_real',2048)))
cc26i = np.asarray(struct.unpack('>512l',s.read('cc_a2_a6_imag',2048)))
cc27r = np.asarray(struct.unpack('>512l',s.read('cc_a2_a7_real',2048)))
cc27i = np.asarray(struct.unpack('>512l',s.read('cc_a2_a7_imag',2048)))
cc28r = np.asarray(struct.unpack('>512l',s.read('cc_a2_a8_real',2048)))
cc28i = np.asarray(struct.unpack('>512l',s.read('cc_a2_a8_imag',2048)))
cc29r = np.asarray(struct.unpack('>512l',s.read('cc_a2_a9_real',2048)))
cc29i = np.asarray(struct.unpack('>512l',s.read('cc_a2_a9_imag',2048)))
cc210r = np.asarray(struct.unpack('>512l',s.read('cc_a2_a10_real',2048)))
cc210i = np.asarray(struct.unpack('>512l',s.read('cc_a2_a10_imag',2048)))
cc211r = np.asarray(struct.unpack('>512l',s.read('cc_a2_a11_real',2048)))
cc211i = np.asarray(struct.unpack('>512l',s.read('cc_a2_a11_imag',2048)))

#Antenna 3 Cross 4 - 11
cc34r = np.asarray(struct.unpack('>512l',s.read('cc_a3_a4_real',2048)))
cc34i = np.asarray(struct.unpack('>512l',s.read('cc_a3_a4_imag',2048)))
cc35r = np.asarray(struct.unpack('>512l',s.read('cc_a3_a5_real',2048)))
cc35i = np.asarray(struct.unpack('>512l',s.read('cc_a3_a5_imag',2048)))
cc36r = np.asarray(struct.unpack('>512l',s.read('cc_a3_a6_real',2048)))
cc36i = np.asarray(struct.unpack('>512l',s.read('cc_a3_a6_imag',2048)))
cc37r = np.asarray(struct.unpack('>512l',s.read('cc_a3_a7_real',2048)))
cc37i = np.asarray(struct.unpack('>512l',s.read('cc_a3_a7_imag',2048)))
cc38r = np.asarray(struct.unpack('>512l',s.read('cc_a3_a8_real',2048)))
cc38i = np.asarray(struct.unpack('>512l',s.read('cc_a3_a8_imag',2048)))
cc39r = np.asarray(struct.unpack('>512l',s.read('cc_a3_a9_real',2048)))
cc39i = np.asarray(struct.unpack('>512l',s.read('cc_a3_a9_imag',2048)))
cc310r = np.asarray(struct.unpack('>512l',s.read('cc_a3_a10_real',2048)))
cc310i = np.asarray(struct.unpack('>512l',s.read('cc_a3_a10_imag',2048)))
cc311r = np.asarray(struct.unpack('>512l',s.read('cc_a3_a11_real',2048)))
cc311i = np.asarray(struct.unpack('>512l',s.read('cc_a3_a11_imag',2048)))

#Antenna 4 Cross 5 - 11
cc45r = np.asarray(struct.unpack('>512l',s.read('cc_a4_a5_real',2048)))
cc45i = np.asarray(struct.unpack('>512l',s.read('cc_a4_a5_imag',2048)))
cc46r = np.asarray(struct.unpack('>512l',s.read('cc_a4_a6_real',2048)))
cc46i = np.asarray(struct.unpack('>512l',s.read('cc_a4_a6_imag',2048)))
cc47r = np.asarray(struct.unpack('>512l',s.read('cc_a4_a7_real',2048)))
cc47i = np.asarray(struct.unpack('>512l',s.read('cc_a4_a7_imag',2048)))
cc48r = np.asarray(struct.unpack('>512l',s.read('cc_a4_a8_real',2048)))
cc48i = np.asarray(struct.unpack('>512l',s.read('cc_a4_a8_imag',2048)))
cc49r = np.asarray(struct.unpack('>512l',s.read('cc_a4_a9_real',2048)))
cc49i = np.asarray(struct.unpack('>512l',s.read('cc_a4_a9_imag',2048)))
cc410r = np.asarray(struct.unpack('>512l',s.read('cc_a4_a10_real',2048)))
cc410i = np.asarray(struct.unpack('>512l',s.read('cc_a4_a10_imag',2048)))
cc411r = np.asarray(struct.unpack('>512l',s.read('cc_a4_a11_real',2048)))
cc411i = np.asarray(struct.unpack('>512l',s.read('cc_a4_a11_imag',2048)))

#Antenna 5 Cross 6 - 11
cc56r = np.asarray(struct.unpack('>512l',s.read('cc_a5_a6_real',2048)))
cc56i = np.asarray(struct.unpack('>512l',s.read('cc_a5_a6_imag',2048)))
cc57r = np.asarray(struct.unpack('>512l',s.read('cc_a5_a7_real',2048)))
cc57i = np.asarray(struct.unpack('>512l',s.read('cc_a5_a7_imag',2048)))
cc58r = np.asarray(struct.unpack('>512l',s.read('cc_a5_a8_real',2048)))
cc58i = np.asarray(struct.unpack('>512l',s.read('cc_a5_a8_imag',2048)))
cc59r = np.asarray(struct.unpack('>512l',s.read('cc_a5_a9_real',2048)))
cc59i = np.asarray(struct.unpack('>512l',s.read('cc_a5_a9_imag',2048)))
cc510r = np.asarray(struct.unpack('>512l',s.read('cc_a5_a10_real',2048)))
cc510i = np.asarray(struct.unpack('>512l',s.read('cc_a5_a10_imag',2048)))
cc511r = np.asarray(struct.unpack('>512l',s.read('cc_a5_a11_real',2048)))
cc511i = np.asarray(struct.unpack('>512l',s.read('cc_a5_a11_imag',2048)))

#Antenna 6 Cross 7 - 11
cc67r = np.asarray(struct.unpack('>512l',s.read('cc_a6_a7_real',2048)))
cc67i = np.asarray(struct.unpack('>512l',s.read('cc_a6_a7_imag',2048)))
cc68r = np.asarray(struct.unpack('>512l',s.read('cc_a6_a8_real',2048)))
cc68i = np.asarray(struct.unpack('>512l',s.read('cc_a6_a8_imag',2048)))
cc69r = np.asarray(struct.unpack('>512l',s.read('cc_a6_a9_real',2048)))
cc69i = np.asarray(struct.unpack('>512l',s.read('cc_a6_a9_imag',2048)))
cc610r = np.asarray(struct.unpack('>512l',s.read('cc_a6_a10_real',2048)))
cc610i = np.asarray(struct.unpack('>512l',s.read('cc_a6_a10_imag',2048)))
cc611r = np.asarray(struct.unpack('>512l',s.read('cc_a6_a11_real',2048)))
cc611i = np.asarray(struct.unpack('>512l',s.read('cc_a6_a11_imag',2048)))

#Antenna 7 Cross 8 - 11
cc78r = np.asarray(struct.unpack('>512l',s.read('cc_a7_a8_real',2048)))
cc78i = np.asarray(struct.unpack('>512l',s.read('cc_a7_a8_imag',2048)))
cc79r = np.asarray(struct.unpack('>512l',s.read('cc_a7_a9_real',2048)))
cc79i = np.asarray(struct.unpack('>512l',s.read('cc_a7_a9_imag',2048)))
cc710r = np.asarray(struct.unpack('>512l',s.read('cc_a7_a10_real',2048)))
cc710i = np.asarray(struct.unpack('>512l',s.read('cc_a7_a10_imag',2048)))
cc711r = np.asarray(struct.unpack('>512l',s.read('cc_a7_a11_real',2048)))
cc711i = np.asarray(struct.unpack('>512l',s.read('cc_a7_a11_imag',2048)))

#Antenna 8 Cross 9 - 11
cc89r = np.asarray(struct.unpack('>512l',s.read('cc_a8_a9_real',2048)))
cc89i = np.asarray(struct.unpack('>512l',s.read('cc_a8_a9_imag',2048)))
cc810r = np.asarray(struct.unpack('>512l',s.read('cc_a8_a10_real',2048)))
cc810i = np.asarray(struct.unpack('>512l',s.read('cc_a8_a10_imag',2048)))
cc811r = np.asarray(struct.unpack('>512l',s.read('cc_a8_a11_real',2048)))
cc811i = np.asarray(struct.unpack('>512l',s.read('cc_a8_a11_imag',2048)))

#Antenna 9 Cross 10 - 11
cc910r = np.asarray(struct.unpack('>512l',s.read('cc_a9_a10_real',2048)))
cc910i = np.asarray(struct.unpack('>512l',s.read('cc_a9_a10_imag',2048)))
cc911r = np.asarray(struct.unpack('>512l',s.read('cc_a9_a11_real',2048)))
cc911i = np.asarray(struct.unpack('>512l',s.read('cc_a9_a11_imag',2048)))

#Antenna 10 Cross 11
cc1011r = np.asarray(struct.unpack('>512l',s.read('cc_a10_a11_real',2048)))
cc1011i = np.asarray(struct.unpack('>512l',s.read('cc_a10_a11_imag',2048)))


#--------------------------------------------------------------------------------------------------------------------------------------
#Determination of the Magnitude Responses of the Autocorrelations of each input
#Phase Responses not solved for to save BRAM Space (no accumulation & storage of imaginary data stream)
#as Phase Responses are 0 for Autocorrelations

#Autocorrelation of 0
magac0 = abs(ac0)
#Autocorrelation of 1
magac1 = abs(ac1)
#Autocorrelation of 2
magac2 = abs(ac2)
#Autocorrelation of 3
magac3 = abs(ac3)
#Autocorrelation of 4
magac4 = abs(ac4)
#Autocorrelation of 5
magac5 = abs(ac5)
#Autocorrelation of 6
magac6 = abs(ac6)
#Autocorrelation of 7
magac7 = abs(ac7)
#Autocorrelation of 8
magac8 = abs(ac8)
#Autocorrelation of 9
magac9 = abs(ac9)
#Autocorrelation of 10
magac10 = abs(ac10)
#Autocorrelation of 11
magac11 = abs(ac11)

#--------------------------------------------------------------------------------------------------------------------------------------
#Recombing real and imaginary parts of the Accumulated Cross Correlations 
#& Solving for Magnitudes and Phase Responses of the Cross Correlations

#Cross Correlation of 0 and 1
cc01rl = list(cc01r)
cc01il = list(cc01i)
cc01 = merge(cc01rl,cc01il)
magcc01 = abs(cc01)
phasecc01 = np.angle(cc01)*180/np.pi
#Cross Correlation of 0 and 2
cc02rl = list(cc02r)
cc02il = list(cc02i)
cc02 = merge(cc02rl,cc02il)
magcc02 = abs(cc02)
phasecc02 = np.angle(cc02)*180/np.pi
#Cross Correlation of 0 and 3
cc03rl = list(cc03r)
cc03il = list(cc03i)
cc03 = merge(cc03rl,cc03il)
magcc03 = abs(cc03)
phasecc03 = np.angle(cc03)*180/np.pi
#Cross Correlation of 1 and 2
cc12rl = list(cc12r)
cc12il = list(cc12i)
cc12 = merge(cc12rl,cc12il)
magcc12 = abs(cc12)
phasecc12 = np.angle(cc12)*180/np.pi
#Cross Correlation of 1 and 3
cc13rl = list(cc13r)
cc13il = list(cc13i)
cc13 = merge(cc13rl,cc13il)
magcc13 = abs(cc13)
phasecc13 = np.angle(cc13)*180/np.pi
#Cross Correlation of 2 and 3
cc23rl = list(cc23r)
cc23il = list(cc23i)
cc23 = merge(cc23rl,cc23il)
magcc23 = abs(cc23)
phasecc23 = np.angle(cc23)*180/np.pi






#--------------------------------------------------------------------------------------------------------------------------------------
print "Plotting Data"
#Autocorrelation Plots
plt.figure(1)
plt.title('Autocorrelation of Antenna 0')
plt.title('Magnitude Response of AC of 0')
plt.plot(fn,magac0,'g')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.figure(2)
plt.title('Autocorrelation of Antenna 1')
plt.title('Magnitude Response of AC of 1')
plt.plot(fn,magac1,'r')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.figure(3)
plt.title('Autocorrelation of Antenna 2')
plt.title('Magnitude Response of AC of 2')
plt.plot(fn,magac2,'c')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)


plt.figure(4)
plt.title('Autocorrelation of Antenna 3')
plt.title('Magnitude Response of AC of 3')
plt.plot(fn,magac3,'y')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

#--------------------------------------------------------------------------------------------------------------------------------------
#Cross Correlation Plots

plt.figure(5)
plt.title('Cross Correlation of Antennas 0 & 1')
plt.subplot(211)
plt.title('Magnitude Response of CC of 0 & 1')
plt.plot(fn,magcc01,'k')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 0 & 1')
plt.plot(fn,phasecc01,'k')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(6)
plt.title('Cross Correlation of Antennas 0 & 2')
plt.subplot(211)
plt.title('Magnitude Response of CC of 0 & 2')
plt.plot(fn,magcc02,'m')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 0 & 2')
plt.plot(fn,phasecc02,'m')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(7)
plt.title('Cross Correlation of Antennas 0 & 3')
plt.subplot(211)
plt.title('Magnitude Response of CC of 0 & 3')
plt.plot(fn,magcc03,'k')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 0 & 3')
plt.plot(fn,phasecc03,'k')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(8)
plt.title('Cross Correlation of Antennas 1 & 2')
plt.subplot(211)
plt.title('Magnitude Response of CC of 1 & 2')
plt.plot(fn,magcc12,'k')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 1 & 2')
plt.plot(fn,phasecc12,'k')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(9)
plt.title('Cross Correlation of Antennas 1 & 3')
plt.subplot(211)
plt.title('Magnitude Response of CC of 1 & 3')
plt.plot(fn,magcc13,'m')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 1 & 3')
plt.plot(fn,phasecc13,'m')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(10)
plt.title('Cross Correlation of Antennas 2 & 3')
plt.subplot(211)
plt.title('Magnitude Response of CC of 2 & 3')
plt.plot(fn,magcc23,'k')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 2 & 3')
plt.plot(fn,phasecc23,'k')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.show()
