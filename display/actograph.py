import numpy as np
from datetime import date, datetime, time, timedelta
import cPickle as pickle
import matplotlib.pyplot as plt
import pdb
import os

sbj_ids = ["d6532718", "cb46fd46","e70923c4", "fcb01f7a", "a86a4375", "c95c1e82" ]
day_starts = [date(2015,6,11), date(2015,4,3), date(2015,9,11), date(2015,3,5), date(2015,2,26), date(2015,5,29)]

time_s = time(8,0,0)

day_range = [3,12]

vid_start_end = "C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\vid_real_time\\"
graphs = []
f, plots=plt.subplots(1)
for sbj, sbj_id in enumerate(sbj_ids):
    day_start = day_starts[sbj]
    mvmt_loc="E:\\mvmt\\" + sbj_id + "\\"
    sound_loc="E:\\sound\\" + sbj_id + "\\"

    for i in xrange(4):
        day = day_start + timedelta(days=i)
        print "On day " + str(day) + " for subject " + sbj_id
        start_time = datetime.combine(day, time_s)
        actograph = np.zeros(shape=(24*61,3))
        actograph[:,:] = 255

        for d in range(day_range[0],day_range[1]+1):
            if os.path.isfile(vid_start_end + sbj_id + "_" + str(d) + ".p"):
                date_file = pickle.load(open(vid_start_end + sbj_id + "_" + str(d) + ".p", "rb"))
                for s, start in enumerate(date_file["start"]):
                    if start > start_time and start < (start_time + timedelta(hours=24)):
                        if(os.path.isfile(sound_loc + str(d) + "\\" + sbj_id + "_" +
                                                     str(d) + "_" + str(s).zfill(4) + ".p") and
                           os.path.isfile(mvmt_loc + sbj_id + "_" + str(d) + "_" + str(s).zfill(4) + ".p") ):
                            mvmt = pickle.load(open(mvmt_loc + sbj_id + "_" + str(d) + "_" + str(s).zfill(4) + ".p","rb"))
                            start_point = (start-start_time).seconds/60
                            mvmt_vals = mvmt[::30*60]*2
                            mvmt_vals[np.where(mvmt_vals<1.5)[0]] = 0
                            actograph[start_point:start_point + len(mvmt[::30*60]),0] = 255-mvmt_vals*50

                            sound = pickle.load(open(sound_loc + str(d) + "\\" + sbj_id + "_" +
                                                     str(d) + "_" + str(s).zfill(4) + ".p","rb"))
                            sound_vals = sound[::30*60]/(3.6*10**11)
                            sound_vals[np.where(sound_vals<0.95)[0]] = 0
                            actograph[start_point:start_point + len(sound[::30*60]),1] = 255-sound_vals*50


        #y, x = np.mgrid[slice(0, 20, 1),
        #                slice(0, actograph.shape[1], 1)]
        #mvmt_img = scipy.misc.toimage(np.tile(actograph[0,:], (80,1)), cmin=1, cmax=3)
        #Z_mvmt=np.tile(actograph[0,:], (80,1))
        #Z_sound=np.tile(actograph[1,:], (80,1))
        #Z_sound = np.ma.masked_where(Z_sound<1.1, Z_sound)
        graphs.append(np.tile(actograph/255.0, (20, 1, 1)))
#pdb.set_trace()
plots.imshow(np.vstack(graphs))
plots.axes.get_yaxis().set_visible(False)
plots.axes.get_xaxis().set_visible(False)
plots.set_ylabel("Day " + str(i+3))


#plt.imshow(Z_sound,  vmin=1.5, vmax=4, cmap=plt.cm.Blues, alpha=0.5)
#plt.pcolormesh(x,y,np.tile(actograph[1,:], (20,1)), cmap=plt.cm.Blues, vmin=1, vmax=3, alpha=0.25)
#plt.axis([x.min(), x.max(), y.min(), y.max()])
#plt.colorbar()
plots.set_title("Sample Subject Activity")
plots.set_xlabel("Time")
hours = [str((start_time + timedelta(minutes=ti)).hour) for ti in range(len(actograph))[::100]]
plots.axes.get_xaxis().set_visible(True)
plots.set_xticks(range(len(actograph))[::100], hours)
f.tight_layout()
#plt.show()
plt.savefig("E:\\mvmt\\" + "actograph.png")
plt.close()

