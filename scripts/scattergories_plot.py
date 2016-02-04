import matplotlib.pyplot as plt
import matplotlib
import cPickle as pickle
import numpy as np

matplotlib.rc('font', family='serif')

def close_count(num_array, val, thresh):
    cnt = 0
    for n in num_array:
        if abs(n-val)<thresh and n>0:
            cnt += 1 + cnt
    return cnt

sbj_id_all = ["d6532718", "cb46fd46", "fcb01f7a", "a86a4375", "c95c1e82", "e70923c4"]
mymap = plt.get_cmap("rainbow")
colorspace = np.r_[np.linspace(0.1, 1, 6), np.linspace(0.1, 2, 6)]
colors = mymap(colorspace)
level = '2'
total_percentiles = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}

end1 =  np.mean([len(sbj_id_all)/1.5,len(sbj_id_all)])
end2 =  np.mean([len(sbj_id_all)/1.5 + len(sbj_id_all),2*len(sbj_id_all)])
end3 =  3*len(sbj_id_all)

plt.figure(figsize=(9,4))
plt.axvspan(-1, end1, facecolor='0.2', alpha=0.1)
#plt.axvspan(end1,end2, facecolor='green', alpha=0.1)
plt.axvspan(end2,end3, facecolor='0.2', alpha=0.1)

for sbj, sbj_id in enumerate(sbj_id_all):
    label_accuracy_loc="C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\validation_fewer_frequencies\\" + sbj_id + "\\"
    f1_percentile = pickle.load(open(label_accuracy_loc + "percentile_f1"
                                     + "_" + level + ".p", "rb"))

    f1_counts = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
    for key, args in f1_percentile.iteritems():
        for i,a in enumerate(args):
            f1_counts[key].append(close_count(args[i:], a, 1))
            if a>=0:
                total_percentiles[key].append(a)

    num_points = len(f1_percentile['Mvmt'])
    #pdb.set_trace()
    print sbj_id
    print f1_percentile
    plt.scatter([0],
                [-2], c=colors[sbj], s=30, label="Subject " + str(sbj+1))
    plt.scatter(np.repeat(sbj/1.5,num_points),(f1_percentile['Mvmt']), color=colors[sbj],
                edgecolors='black', s=np.array(f1_counts['Mvmt'])*30, zorder=3)
#    plt.vlines(np.mean([len(sbj_id_all)/1.5, len(sbj_id_all)]),0,110, colors='gray')
    plt.scatter(np.repeat(sbj/1.5+len(sbj_id_all),num_points),
                (f1_percentile['Sound']), edgecolors='black',
                color=colors[sbj],s=np.array(f1_counts['Sound'])*30, zorder=3)
#    plt.vlines(np.mean([2*len(sbj_id_all)/1.5, 2*len(sbj_id_all)])+1,0,110, colors='gray')
    plt.scatter(np.repeat(sbj/1.5+2*len(sbj_id_all),num_points),
                (f1_percentile['Rest']), edgecolors='black',
                color=colors[sbj], s=np.array(f1_counts['Rest'])*30, zorder=3)

    plt.ylim([0,110])
    plt.xlim([-1,np.mean([len(sbj_id_all)/1.5+ len(sbj_id_all)*2, 3*len(sbj_id_all)])])

    plt.xticks([len(sbj_id_all)/2.0/1.5,len(sbj_id_all)/2.0/1.5+len(sbj_id_all),
                len(sbj_id_all)/2.0/1.5+2*len(sbj_id_all)], ['Movement', "Speech", "Rest"])
    plt.xlabel("Categories")
    plt.ylabel("F1 score comparison against shuffle \n (Percentile)  ")
    plt.tight_layout()
plt.hlines(np.median(total_percentiles["Mvmt"]),0, (len(sbj_id_all)-1)/1.5, label="Median")
plt.hlines(np.median(total_percentiles["Sound"]),len(sbj_id_all),len(sbj_id_all)+(len(sbj_id_all)-1)/1.5)
plt.hlines(np.median(total_percentiles["Rest"]),2*len(sbj_id_all),2*len(sbj_id_all)+(len(sbj_id_all)-1)/1.5)

plt.legend(bbox_to_anchor=(0., 1.02, 1.27, 0.), scatterpoints = 1)
plt.savefig("C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\validation_fewer_frequencies\\percentile_scattergories_f1_" + str(level) + ".png",
            bbox_inches='tight')
#plt.show()