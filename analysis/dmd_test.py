import mne.io
import dmd
import numpy as np
import matplotlib.pyplot as plt
import pdb

datafile = "C:\\Users\\Nancy\\Documents\data\\d6532718\\d6532718_4.edf"
edf = mne.io.read_raw_edf(datafile)
n_channels = len(edf.ch_names)
Fmodes_all = np.zeros(shape=(100*6,n_channels-1))
for w in xrange(100*6):
    if w % 100==0:
        print w
    data, time = edf[1:,(w)*1000:(w+1)*1000]

    Fmodes, b, V, omega = dmd.dmd(data, dt=0.01, return_vandermonde=True, return_amplitudes=True)
    Fmodes_all[w] = Fmodes[10]

Fmodes_all[np.where(np.abs(Fmodes_all)>0.1)]=0
plt.imshow(Fmodes_all.T, aspect=20)
plt.colorbar()
plt.show()
pdb.set_trace()
