__author__ = 'wangnxr'

from pyESig2.cluster import truncated_hier_cluster_train_single_day
from pyESig2.vid import aggregate
from pyESig2.validation import check_labels
from pyESig2.analysis import correlate_signals
from pyESig2.annotation import extract_labels
from pyESig2.vid.misc_funcs import has_video
from pyESig2.unsupervised.reverse_pca import back_project
from pyESig2.util.summary_stats import print_averages
from scipy.stats import percentileofscore
from numpy import random
import matplotlib.pyplot as plt
import matplotlib
import cPickle as pickle
import glob
import pdb
import numpy as np
import csv
import tabulate
from datetime import date, datetime, time, timedelta
import cPickle as pickle
import os
import matplotlib.dates as mdates
import matplotlib

random.seed()
#Raw_sources
level = '2'
sbj_id_all = ["d6532718", "cb46fd46", "fcb01f7a", "a86a4375", "c95c1e82", "e70923c4" ]
dates_all = [[4,5,6,7], [7,8,9,10], [8,10,11,12], [4,5,6,7], [4,5,6,7], [4,5,6,7]]

final_accuracy = []
final_accuracy_random = []
final_percentile_accuracy = []
final_accuracy_random_std = []
final_f1 = []
final_recall = []
final_specificity = []
percentile_save_file = csv.writer(open("C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\train_single_day\\percentile_" + level + ".csv", "wb"))
for s, sbj_id in enumerate(sbj_id_all):
    dates=dates_all[s]
    video_loc="D:\\NancyStudyData\\ecog\\raw\\" + sbj_id + "\\"
    ecog_feature_loc="D:\\ecog_processed\\d_reduced\\"
    mvmt_loc="E:\\mvmt\\" + sbj_id + "\\"
    sound_loc="E:\\sound\\" + sbj_id + "\\"
    label_loc="C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\manual_annotations\\tracks\\"
    disconnect_file_loc="C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\disconnect_times\\"
    vid_start_end = "C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\vid_real_time\\"

    #Save_locations

    ecog_cluster_loc= "E:\\cluster_results_train_single_day\\" + sbj_id + "\\"
    extracted_label_loc="C:\\Users\\wangnxr\Documents\\rao_lab\\video_analysis\\train_single_day\\manual_annotations\\extracted_labels_reduced\\"
    extracted_random_label_loc="C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\train_single_day\\manual_annotations\\extracted_labels_random\\"
    label_accuracy_loc="C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\train_single_day\\validation\\" + sbj_id + "\\"
    back_project_loc="C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\train_single_day\\back_project\\"

    #Internal_save_variables
    best_corr_clusters=[]

    #Generate clusters
    print "Starting: Clustering"
    #truncated_hier_cluster_train_single_day.hier_cluster_main(sbj_id,dates,ecog_feature_loc,ecog_cluster_loc)
    print "Finished: Clustering"

    # #Plot Clusters
    # #
    # font = {'family' : 'serif',
    #     'size'   : 15}
    #
    # matplotlib.rc('font', **font)
    #
    # time_s = time(9,0,0)
    # day = date(2015,6,11)
    # start_time = datetime.combine(day, time_s)
    # for lev in [2]:
    #     f, plots=plt.subplots(1)
    #     f.set_size_inches(20.5, 10.5)
    #
    #     cluster_plt_raw = pickle.load(open(ecog_cluster_loc + sbj_id + "_" + str(7) + "_" + str(lev) + ".p", "rb"))
    #     cluster_plt = np.zeros(shape=(cluster_plt_raw.shape[0]/10+1, cluster_plt_raw.shape[1]))
    #     for c in xrange(cluster_plt_raw.shape[1]):
    #         cluster_plt[:,c] = np.array([np.mean(cluster_plt_raw[x:x+10,c])/8.0 for x in range(0,cluster_plt_raw.shape[0],10)])
    #     xlims = [start_time + timedelta(seconds=x*16*5) for x in [0,cluster_plt.shape[0]/5*10+1]]
    #     xlims = mdates.date2num(xlims)
    #     index = np.argsort(cluster_plt[:,:].sum(axis=0))
    #
    #     for c in [4,0,7]:
    #         #if c==1:
    #          #   leg = "Rest"
    #          #   color_c = "gray"
    #         #if c==0:
    #         #    leg = "Non Rest"
    #         #    color_c = "purple"
    #         if c==7:
    #             leg = "Rest"
    #             color_c = "gray"
    #             t=60*60*1.975
    #             marker_at=start_time + timedelta(seconds=t)
    #             m=t/16/10
    #             marker_shape = 'v'
    #         elif c==0:
    #             leg = "Speech"
    #             color_c = "green"
    #             t=60*60*7.6
    #             marker_at=start_time + timedelta(seconds=t)
    #             m=t/16/10
    #             marker_shape = 'o'
    #         else:
    #             leg = "Movement"
    #             color_c = "orange"
    #             t=60*60*3.645
    #             marker_at=start_time + timedelta(seconds=t)
    #             marker_shape = 's'
    #             m=t/16/10
    #         plots.plot([start_time + timedelta(seconds=x*16*10) for x in range(0,cluster_plt.shape[0])]
    #                    ,cluster_plt[:,c].T, label = leg, color=color_c)
    #         plots.plot(marker_at, 0.7, color='red', marker=marker_shape, markersize=10, mec=None )
    #     plots.xaxis_date()
    #     date_format = mdates.DateFormatter('%I:%M %p')
    #     plots.xaxis.set_major_formatter(date_format)
    #     plots.set_ylim([0,1])
    #     #plots.xlim(xlims)
    #     #leg = plots.legend(loc=0)
    #     #for legobj in leg.legendHandles:
    #     #    legobj.set_linewidth(2.0)
    #     # This simply sets the x-axis data to diagonal so it fits better.
    #     f.autofmt_xdate()
    #
    #     plt.ylabel("Fraction of occurence")
    #     plt.title("Level " + str(lev+1))
    #     #plt.tight_layout()
    #     plt.show()
    # pdb.set_trace()
    #Aggregate sound files
    for date in dates:
        print "Starting: Sound aggregation for day " + str(date)
        has_video_array=has_video(disconnect_file_loc + sbj_id + "_" + str(date) + ".txt")
        aggregate.aggregate(sbj_id, date, sound_loc + str(date) + "\\",
                            sound_loc + str(date) + "\\", has_video_array)

    #Aggregate mvmt files
    for date in dates:
        print "Starting: Mvmt aggregation for day " + str(date)
        has_video_array=has_video(disconnect_file_loc + sbj_id + "_" + str(date) + ".txt")

        aggregate.aggregate(sbj_id, date, mvmt_loc,
                            mvmt_loc, has_video_array)

    #Correlate clusters
    for date in dates:
        print "Starting: Correlations for day " + str(date)
        best_corr_clusters.append(correlate_signals.correlate( sound_loc  + str(date) + "\\" + sbj_id + "_" + str(date) + ".p",
                                                               mvmt_loc + sbj_id + "_" + str(date) + ".p",
                                     ecog_cluster_loc + sbj_id + "_" + str(date) + "_" + level + "_train_single_day.p"))

    #Extract labels
    for date in dates:
        print "Starting: Extracting labels for day " + str(date)
        extract_labels.extract_reduced_labels(sbj_id, date, label_loc, video_loc, extracted_label_loc)


    #Check labels
    for d, date in enumerate(dates):
        print "Starting: Checking labels for day " + str(date)
        time_correspondence_file = vid_start_end + sbj_id + "_" + str(date) + ".p"
        condensed_cluster_file = ecog_cluster_loc + sbj_id + "_" + str(date) + "_" + level + "_train_single_day.p"
        cluster_file = ecog_cluster_loc + sbj_id + "_" + str(date) + "_train_single_day.p"
        check_labels.label_accuracy(sbj_id, date, extracted_label_loc, extracted_random_label_loc,
                       condensed_cluster_file, time_correspondence_file, label_accuracy_loc + level + "_")
        check_labels.cluster_label_accuracy(sbj_id, date, extracted_label_loc, best_corr_clusters[0],
                                            condensed_cluster_file,
                                            time_correspondence_file,
                                            cluster_file,
                                            label_accuracy_loc + level + "_")
    #Label_histograms
    # for d, date in enumerate(dates):
    #     print "Starting: Generating histograms for day " + str(date)
    #     time_correspondence_file =  vid_start_end + sbj_id + "_" + str(date) + ".p"
    #     cluster_file = ecog_cluster_loc + sbj_id + "_" + str(date) + "_train_single_day.p"
    #     check_labels.label_histogram_cluster(sbj_id, date, extracted_label_loc, int(level),
    #                                          best_corr_clusters[0], cluster_file,
    #                                          time_correspondence_file, label_accuracy_loc + level + "_")
    #
    # #Back project cluster center
    # train_day = dates[0]
    # for d, date in enumerate(dates):
    #     print "Starting: Back projecting for day " + str(date)
    #     pca_model = ecog_feature_loc + "transformed_pca_model_" + sbj_id + "_" + str(train_day) + ".p"
    #     cluster_center_file = ecog_cluster_loc + sbj_id + "_" + str(date) + "_" + level + "_centers_train_single_day.p"
    #
    #     back_project(pca_model, cluster_center_file,
    #                  best_corr_clusters[0], back_project_loc + sbj_id + "_" + str(date) + "_" + level + "_")

       #Summary statistics

    #Normal
    print sbj_id
    total_recall = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
    total_precision = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
    total_specificity = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
    total_f1 = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
    total_accuracy = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
    tracks = ["Mvmt", "Sound", "Rest", "Other"]
    for file in [(label_accuracy_loc) +  "\\" + level + "_" + sbj_id + "_" + str(date) + "_results.p" for date in dates]:

        summaries = pickle.load(open(file, "rb"))
        for summary in summaries:
            ind = summary["track"]
            total_recall[ind].append(summary['recall_score'])
            total_precision[ind].append(summary['precision_score'])
            total_specificity[ind].append(summary['specificity_score'])
            total_f1[ind].append(summary['f1_score'])

            total_accuracy[ind].append(summary['accuracy_score'])


    final_accuracy.append(total_accuracy)
    final_f1.append(total_f1)
    final_recall.append(total_recall)
    final_specificity.append(total_specificity)
    print "Recall"
    print_averages(total_recall)
    print "Precision"
    print_averages(total_precision)
    print "Specificity"
    print_averages(total_precision)
    print "f1"
    print_averages(total_f1)
    print "accuracy"
    print_averages(total_accuracy)

    # print "------------------------RANDOM------------------------------------"
    # #random
    # total_recall_random = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
    # total_precision_random = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
    # total_f1_random = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
    # total_accuracy_random = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
    # for file in glob.glob((label_accuracy_loc) +  "\\" + level + "_" + "*_results_random.p"):
    #     summaries = pickle.load(open(file, "rb"))
    #     for summary in summaries:
    #         ind = summary["track"]
    #         total_recall_random[ind].append(np.nanmean(summary['recall_score']))
    #         total_precision_random[ind].append(np.nanmean(summary['precision_score']))
    #         total_f1_random[ind].append(np.nanmean(summary['f1_score']))
    #         total_accuracy_random[ind].append(summary['accuracy_score'])
    # print "Recall"
    # print_averages(total_recall_random)
    # print "Precision"
    # print_averages(total_precision_random)
    # print "f1"
    # print_averages(total_f1_random)

    print "------------------------Percentile of f1 score in RANDOM------------------------------------"

    total_f1_percentile = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
    for file in [(label_accuracy_loc) +  "\\" + level + "_" + sbj_id + "_" + str(date) + "_results_random.p" for date in dates]:
        filename = file.split("\\")[-1]
        date = filename.split("_")[2]
        #print date
        summaries = pickle.load(open(label_accuracy_loc + "\\"
                                     + level +"_" + sbj_id + "_" + date + "_results.p", "rb"))
        summaries_random = pickle.load(open(file, "rb"))

        for s, summary in enumerate(summaries):
            ind = summary["track"]
            if summary['f1_score']==-1:
                total_f1_percentile[ind].append(-1)
            else:
                percentile = percentileofscore(summaries_random[s]['f1_score'],summary['f1_score'])
                total_f1_percentile[ind].append(percentile)
    pickle.dump(total_f1_percentile, open(label_accuracy_loc + "percentile_f1_" + level + ".p", "wb"))
    percentile_save_file.writerow([sbj_id])
    for key, val in total_f1_percentile.items():
        percentile_save_file.writerow([key, val])

    print "f1"
    #print_averages(total_f1_percentile)
    print total_f1_percentile

    print "------------------------Percentile of accuracy score in RANDOM------------------------------------"

    total_accuracy_percentile = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
    total_accuracy_random = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
    total_accuracy_random_std = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
    for file in [(label_accuracy_loc) +  "\\" + level + "_" + sbj_id + "_" + str(date) + "_results_random.p" for date in dates]:
        filename = file.split("\\")[-1]
        date = filename.split("_")[2]
        #print date
        summaries = pickle.load(open(label_accuracy_loc + "\\"
                                     + level +"_" + sbj_id + "_" + date + "_results.p", "rb"))
        summaries_random = pickle.load(open(file, "rb"))

        for s, summary in enumerate(summaries):
            ind = summary["track"]
            if summary['accuracy_score']==-1:
                total_accuracy_percentile[ind].append(-1)
            else:
                percentile = percentileofscore(summaries_random[s]['accuracy_score'],summary['accuracy_score'])
                total_accuracy_random[ind].append(np.mean(summaries_random[s]['accuracy_score']))
                total_accuracy_random_std[ind].append(np.std(summaries_random[s]['accuracy_score']))
                total_accuracy_percentile[ind].append(percentile)
    pickle.dump(total_accuracy_percentile, open(label_accuracy_loc + "percentile_accuracy_" + level + ".p", "wb"))
    percentile_save_file.writerow([sbj_id])
    for key, val in total_accuracy_percentile.items():
        percentile_save_file.writerow([key, val])
    final_percentile_accuracy.append(total_accuracy_percentile)
    final_accuracy_random.append(total_accuracy_random)
    final_accuracy_random_std.append(total_accuracy_random_std)
    print "accuracy"
    #print_averages(total_f1_percentile)
    print total_accuracy_percentile

#Summary statistics

#Normal
total_recall = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
total_precision = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
total_f1 = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
tracks = ["Mvmt", "Sound", "Rest", "Other"]
for file in [(label_accuracy_loc) +  "\\" + level + "_" + sbj_id + "_" + str(date) + "_results.p" for date in dates]:

    summaries = pickle.load(open(file, "rb"))
    for summary in summaries:
        ind = summary["track"]
        total_recall[ind].append(summary['recall_score'])
        total_precision[ind].append(summary['precision_score'])
        total_f1[ind].append(summary['f1_score'])

print "Recall"
print_averages(total_recall)
print "Precision"
print_averages(total_precision)
print "f1"
print_averages(total_f1)

print "------------------------RANDOM------------------------------------"
#random
total_recall_random = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
total_precision_random = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
total_f1_random = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
for file in[(label_accuracy_loc) +  "\\" + level + "_" + sbj_id + "_" + str(date) + "_results_random.p" for date in dates]:
    summaries = pickle.load(open(file, "rb"))
    for summary in summaries:
        ind = summary["track"]
        total_recall_random[ind].append(np.nanmean(summary['recall_score']))
        total_precision_random[ind].append(np.nanmean(summary['precision_score']))
        total_f1_random[ind].append(np.nanmean(summary['f1_score']))

print "Recall"
print_averages(total_recall_random)
print "Precision"
print_averages(total_precision_random)
print "f1"
print_averages(total_f1_random)

##---latex table

headers = ["Movement", "Speech", "Rest"]
headers = ["Acc", "Rand_acc", "Rand_std", "Percentile"]
table = []
for s, sbj_id in enumerate(sbj_id_all):
    mvmt_acc = np.array(final_accuracy[s]["Mvmt"])
    sound_acc = np.array(final_accuracy[s]["Sound"])
    rest_acc =np.array(final_accuracy[s]["Rest"])

    mvmt_acc_rand = np.array(final_accuracy_random[s]["Mvmt"])
    sound_acc_rand = np.array(final_accuracy_random[s]["Sound"])
    rest_acc_rand =np.array(final_accuracy_random[s]["Rest"])

    mvmt_acc_rand_std = np.array(final_accuracy_random_std[s]["Mvmt"])
    sound_acc_rand_std = np.array(final_accuracy_random_std[s]["Sound"])
    rest_acc_rand_std =np.array(final_accuracy_random_std[s]["Rest"])

    mvmt_pctl = np.array(final_percentile_accuracy[s]["Mvmt"])
    sound_pctl = np.array(final_percentile_accuracy[s]["Sound"])
    rest_pctl =np.array(final_percentile_accuracy[s]["Rest"])
    table.append(["S" + str(s+1), round(np.mean(mvmt_acc[np.where(mvmt_acc>=0)[0]])*100,2),round(np.mean(mvmt_acc_rand[np.where(mvmt_acc_rand>=0)[0]])*100,2),
                                  round(np.mean(mvmt_acc_rand_std[np.where(mvmt_acc_rand_std>=0)[0]])*100,2),round(np.mean(mvmt_pctl[np.where(mvmt_pctl>=0)[0]]),2),
                                  round(np.mean(sound_acc[np.where(sound_acc>=0)[0]])*100,2),round(np.mean(sound_acc_rand[np.where(sound_acc_rand>=0)[0]])*100,2),
                                  round(np.mean(sound_acc_rand_std[np.where(sound_acc_rand_std>=0)[0]])*100,2),round(np.mean(sound_pctl[np.where(sound_pctl>=0)[0]]),2),
                                  round(np.mean(rest_acc[np.where(rest_acc>=0)[0]])*100,2),round(np.mean(rest_acc_rand[np.where(rest_acc_rand>=0)[0]])*100,2),
                                  round(np.mean(rest_acc_rand_std[np.where(rest_acc_rand_std>=0)[0]])*100,2),round(np.mean(rest_pctl[np.where(rest_pctl>=0)[0]]),2)])
print "Accuracy table"
print tabulate.tabulate(table, headers, tablefmt="latex")

headers = ["Movement", "Speech", "Rest"]
table = []
for s, sbj_id in enumerate(sbj_id_all):
    mvmt_acc = np.array(final_f1[s]["Mvmt"])
    sound_acc = np.array(final_f1[s]["Sound"])
    rest_acc =np.array(final_f1[s]["Rest"])
    table.append(["S" + str(s+1), round(np.mean(mvmt_acc[np.where(mvmt_acc>=0)[0]]),2),
                                  round(np.mean(sound_acc[np.where(sound_acc>=0)[0]]),2),
                                  round(np.mean(rest_acc[np.where(rest_acc>=0)[0]]),2)])
print "F1 table"
print tabulate.tabulate(table, headers, tablefmt="latex")

headers = ["Specificity", "Sensitivity"]*3
table = []
for s, sbj_id in enumerate(sbj_id_all):
    mvmt_sen = np.array(final_recall[s]["Mvmt"])
    sound_sen = np.array(final_recall[s]["Sound"])
    rest_sen =np.array(final_recall[s]["Rest"])
    mvmt_sp = np.array(final_specificity[s]["Mvmt"])
    sound_sp = np.array(final_specificity[s]["Sound"])
    rest_sp =np.array(final_specificity[s]["Rest"])
    table.append(["S" + str(s+1), round(np.mean(mvmt_sp[np.where(mvmt_sp>=0)[0]])*100,2), round(np.mean(mvmt_sen[np.where(mvmt_sen>=0)[0]])*100,2),
                                  round(np.mean(sound_sp[np.where(sound_sp>=0)[0]])*100,2), round(np.mean(sound_sen[np.where(sound_sen>=0)[0]])*100,2),
                                  round(np.mean(rest_sp[np.where(rest_sp>=0)[0]])*100,2), round(np.mean(sound_sen[np.where(sound_sen>=0)[0]])*100,2),])
print "Sp/sen table"
print tabulate.tabulate(table, headers, tablefmt="latex")