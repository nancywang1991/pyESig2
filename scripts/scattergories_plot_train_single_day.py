import matplotlib.pyplot as plt
import matplotlib
import cPickle as pickle
import numpy as np
import pdb

matplotlib.rc('font', family='serif')

def close_count(num_array, val, thresh):
    cnt = 0
    for n in num_array:
        if abs(n-val)<thresh and n>0:
            cnt += 1 + cnt
    return cnt

sbj_id_all = ["d6532718", "cb46fd46", "fcb01f7a", "a86a4375", "c95c1e82", "e70923c4"]
sbj_id_all = ["d6532718", "cb46fd46", "fcb01f7a", "a86a4375", "c95c1e82", "e70923c4"]
mymap = plt.get_cmap("rainbow")
colorspace = np.r_[np.linspace(0.1, 1, 6), np.linspace(0.1, 2, 6)]
colors = mymap(colorspace)
level = '2'
total_percentiles = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}

end1 =  np.mean([len(sbj_id_all)/2, len(sbj_id_all)])-1
end2 =  np.mean([len(sbj_id_all)/2 + len(sbj_id_all),2*len(sbj_id_all)]) - 2.5
end3 =  np.mean([len(sbj_id_all)/2 + 2*len(sbj_id_all),3*len(sbj_id_all)]) -4

plt.figure(figsize=(9,4))
plt.axvspan(-1, end1, facecolor='0.2', alpha=0.1)
#plt.axvspan(end1,end2, facecolor='green', alpha=0.1)
plt.vlines(end1, 0, 110)
plt.vlines(x=end2, ymin=0, ymax=110, linestyles='dashed')
plt.vlines(x=end3, ymin=0, ymax=110, linestyles='dashed')
#plt.axvspan(end2,end3, facecolor='0.2', alpha=0.1)

f1_counts =  [{"Mvmt":[], "Sound":[], "Rest":[], "Other":[]},{"Mvmt":[], "Sound":[], "Rest":[], "Other":[]},
              {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]},{"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}]

f1_percentile_total = []

sbj_id_all.reverse()
for sbj, sbj_id in enumerate(sbj_id_all):
    label_accuracy_loc="C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\train_single_day\\validation\\" + sbj_id + "\\"
    f1_percentile = pickle.load(open(label_accuracy_loc + "percentile_f1"
                                     + "_" + level + ".p", "rb"))
    f1_percentile_total.append(f1_percentile)

    for d in xrange(4):
        for key, args in f1_percentile.iteritems():
            f1_counts_temp = [f[key][d] for f in f1_percentile_total]
            f1_counts[d][key].insert(0,close_count(f1_counts_temp, f1_counts_temp[-1], 1.5))

sbj_id_all.reverse()
for sbj, sbj_id in enumerate(sbj_id_all):
    label_accuracy_loc="C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\train_single_day\\validation\\" + sbj_id + "\\"
    f1_percentile = pickle.load(open(label_accuracy_loc + "percentile_f1"
                                     + "_" + level + ".p", "rb"))
    f1_percentile_total.append(f1_percentile)

    for d in xrange(4):
        for key, args in f1_percentile.iteritems():
             for i,a in enumerate(args):
                if a>=0:
                    total_percentiles[key].append(a)

    num_points = len(f1_percentile['Mvmt'])
    #pdb.set_trace()
    print sbj_id
    print f1_percentile

    for d in xrange(4):
        plt.scatter(1 + d*(end2-end1)-1.1,(f1_percentile['Mvmt'][d]), color="yellow", marker="o",
                    edgecolors='black', s=np.array(f1_counts[d]['Mvmt'][sbj])*30, zorder=3)
    #    plt.vlines(np.mean([len(sbj_id_all)/1.5, len(sbj_id_all)]),0,110, colors='gray')
        plt.scatter(2.5 + d*(end2-end1)-1.1,
                    (f1_percentile['Sound'][d]), edgecolors='black', marker="o",
                    color="green",s=np.array(f1_counts[d]['Sound'][sbj])*30, zorder=3)
    #    plt.vlines(np.mean([2*len(sbj_id_all)/1.5, 2*len(sbj_id_all)])+1,0,110, colors='gray')
        plt.scatter(4 + d*(end2-end1)-1.1,
                    (f1_percentile['Rest'][d]), edgecolors='black', marker="o",
                    color="gray", s=np.array(f1_counts[d]['Rest'][sbj])*30, zorder=3)

    plt.ylim([0,110])
    plt.xlim([-1,np.mean([len(sbj_id_all)/1.5+ len(sbj_id_all)*2, 3*len(sbj_id_all)])])

    plt.xticks([np.mean([-1, end1]),np.mean([end1, end2]),
                np.mean([end2, end3]), np.mean([end3, np.mean([len(sbj_id_all)/1.5+ len(sbj_id_all)*2, 3*len(sbj_id_all)])])],
                ['Train day', "Test day 1", "Test day 2", "Test day 3"])
    plt.xlabel("Day")
    plt.ylabel("F1 score comparison against shuffle \n (Percentile)  ")
    plt.tight_layout()

plt.scatter([0],
                [-2], color="yellow", s=30, label="Movement", edgecolors='black')
plt.scatter([0],
                [-2], color="green", s=30, label="Speech", edgecolors='black')
plt.scatter([0],
                [-2], color="gray", s=30, label="Rest",edgecolors='black')

plt.hlines(-2,0.8 + d*(end2-end1)-1.1, 1.2 + d*(end2-end1)-1.1, label="Median")

for d in xrange(4):

    pctl_temp = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
    for key, arg in f1_percentile_total[0].iteritems():
        for s in xrange(len(sbj_id_all)):
            if f1_percentile_total[s][key][d] >=0:
                pctl_temp[key].append(f1_percentile_total[s][key][d])
    plt.hlines(np.median(pctl_temp["Mvmt"]),0.7 + d*(end2-end1)-1.1, 1.3 + d*(end2-end1)-1.1, zorder=5)
    plt.hlines(np.median(pctl_temp["Sound"]), 2.2 + d*(end2-end1)-1.1, 2.8 + d*(end2-end1)-1.1, zorder=5)
    plt.hlines(np.median(pctl_temp["Rest"]), 3.7 + d*(end2-end1)-1.1,4.3 + d*(end2-end1)-1.1, zorder=5)

plt.legend(bbox_to_anchor=(0., 1.02, 1.27, 0.), scatterpoints = 1)
plt.savefig("C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\train_single_day\\validation\\percentile_scattergories_f1_" + str(level) + "_train_single.jpg",
            bbox_inches='tight')
#plt.show()