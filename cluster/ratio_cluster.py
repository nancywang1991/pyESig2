import numpy as np
import cPickle as pickle
import pdb
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cm as cm
from datetime import date, datetime, time, timedelta


def activity_bar(activity, colors, start_time, day):
    graph = np.array([colors[c] for c in activity])
    graph = np.tile(graph,(20,1,1))

    f, plots=plt.subplots(1)
    xlims = [start_time + timedelta(minutes=x) for x in [0,24*60]]
    xlims = mdates.date2num(xlims)
    plots.imshow(graph, extent=[xlims[0], xlims[1], 0,100], aspect="auto")
    plots.axes.get_yaxis().set_visible(False)
    plots.axes.get_xaxis().set_visible(False)

    plots.xaxis_date()
    date_format = mdates.DateFormatter('%I:%M %p')
    plots.xaxis.set_major_formatter(date_format)
    plots.set_ylabel("Day %s" % day)
    f.autofmt_xdate()
    plots.set_title("Ratio clustering")
    plots.set_xlabel("Time")
    plots.axes.get_xaxis().set_visible(True)
    plt.show()
    return f, plots

def cluster_scatter(cluster, data, colors, size=0.1):
    fig = plt.figure()
    ax = fig.gca()
    points = np.zeros(shape=(len(data), 2))
    for c in xrange(max(cluster)+1):
        cluster_ind = np.where(cluster==c)[0]
        ax.scatter(data[cluster_ind,0],data[cluster_ind,1], color=colors[c], s=size)
    for c in xrange(max(cluster)+1):
        cluster_ind = np.where(cluster==c)[0]
        points[cluster_ind,:] = ax.transData.transform(data[cluster_ind,:2])
    ax.set_xlabel("Ratio %i:%i Hz" %(4, 9 ))
    ax.set_ylabel("Ratio %i:%i Hz" %(25, 55))
    ax.set_title("Clusters of ECoG power ratios")
    width, height = fig.canvas.get_width_height()
    points[:,1] = height - points[:,1]
    return fig, points, ax


def main(sbj_id, day):
    n_clusters = 5

    time_s = datetime.combine(date(2015,6,11), time(8,0,0))

    colors = cm.rainbow(np.linspace(0, 1, n_clusters))


    vid_start_end = "C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\vid_real_time\\"
    ratio_file_1 = pickle.load(open("E:/ratio_mapping/visualizations/%s_%i_ratio_multi_day_4_9_25_55_comp_0.p" %(sbj_id, day)))
    ratio_file_2 = pickle.load(open("E:/ratio_mapping/visualizations/%s_%i_ratio_multi_day_4_9_25_55_comp_1.p" % (sbj_id, day)))
    ratio_file = np.hstack([ratio_file_1[:-1000], ratio_file_2[:-1000]])
    estimator = KMeans(n_clusters, n_init=10, max_iter=1000)
    labels = estimator.fit_predict(ratio_file)
    fig_scatter, pixel_points, ax = cluster_scatter(labels, ratio_file_1, colors)
    plt.show()
    fig_bar, plots = activity_bar(labels, colors, time_s, 7)
    plt.show()
    return labels, ratio_file, fig_scatter, pixel_points

if __name__=="__main__":
    main("cb46fd46", 7)