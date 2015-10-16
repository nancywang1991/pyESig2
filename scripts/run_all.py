__author__ = 'wangnxr'

from pyESig2.cluster import truncated_hier_cluster
from pyESig2.vid import aggregate
from pyESig2.validation import check_labels
from pyESig2.analysis import correlate_signals
from pyESig2.annotation import extract_labels
from pyESig2.vid.misc_funcs import has_video
from pyESig2.unsupervised.reverse_pca import back_project
from pyESig2.util.summary_stats import print_averages
from scipy.stats import percentileofscore
from numpy import random
import os
import cPickle as pickle
import glob
import pdb
import numpy as np
import csv

random.seed()
#Raw_sources
level = '3'
sbj_id_all = ["d6532718"]#, "cb46fd46", "fcb01f7a", "a86a4375", "c95c1e82", "e70923c4" ]
dates_all = [[4,5]]#, [7,8,9,10],[8,9,10,11,12,16], [4,5,6,7], [4,5,6,7], [4,5,7]]

#sbj_id_all = ["e70923c4"]
#dates_all = [[4,5]]

#sbj_id_all = ["e70923c4"]
#dates_all = [[4,5,6,7]]
percentile_save_file = csv.writer(open("C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\validation\\percentile_" + level + ".csv", "wb"))
for s, sbj_id in enumerate(sbj_id_all):
    dates=dates_all[s]
    video_loc="E:\\" + sbj_id + "\\"
    video_loc="D:\\NancyStudyData\\ecog\\raw\\" + sbj_id + "\\"
    ecog_feature_loc="D:\ecog_processed\d_reduced\\"
    mvmt_loc="E:\mvmt\\" + sbj_id + "\\"
    sound_loc="E:\sound\\" + sbj_id + "\\"
    label_loc="C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\manual_annotations\\tracks\\"
    disconnect_file_loc="C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\disconnect_times\\"
    vid_start_end = "C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\vid_real_time\\"

    #Save_locations

    ecog_cluster_loc= "D:\\cluster_results\\" + sbj_id + "\\"
    extracted_label_loc="C:\\Users\\wangnxr\Documents\\rao_lab\\video_analysis\\manual_annotations\\extracted_labels_reduced\\"
    extracted_random_label_loc="C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\manual_annotations\\extracted_labels_random\\"
    label_accuracy_loc="C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\validation\\" + sbj_id + "\\"
    back_project_loc="C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\back_project\\"

    #Internal_save_variables
    best_corr_clusters=[]

    #Generate clusters
    print "Starting: Clustering"
    truncated_hier_cluster.hier_cluster_main(sbj_id,dates,ecog_feature_loc,ecog_cluster_loc)
    print "Finished: Clustering"
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
                                     ecog_cluster_loc + sbj_id + "_" + str(date) + "_" + level + ".p"))

    #Extract labels
    for date in dates:
        print "Starting: Extracting labels for day " + str(date)
        extract_labels.extract_reduced_labels(sbj_id, date, label_loc, video_loc, extracted_label_loc)


    #Check labels
    for d, date in enumerate(dates):
        print "Starting: Checking labels for day " + str(date)
        time_correspondence_file = vid_start_end + sbj_id + "_" + str(date) + ".p"
        condensed_cluster_file = ecog_cluster_loc + sbj_id + "_" + str(date) + "_" + level + ".p"
        check_labels.label_accuracy(sbj_id, date, extracted_label_loc, extracted_random_label_loc,
                       condensed_cluster_file, time_correspondence_file, label_accuracy_loc + level + "_")
        check_labels.cluster_label_accuracy(sbj_id, date, extracted_label_loc, best_corr_clusters[d],
                                            condensed_cluster_file,
                                            time_correspondence_file,
                                            mvmt_loc + sbj_id + "_" + str(date) + ".p",
                                            sound_loc  + str(date) + "\\" + sbj_id + "_" + str(date) + ".p",
                                            label_accuracy_loc + level + "_")
    #Label_histograms
    for d, date in enumerate(dates):
        print "Starting: Generating histograms for day " + str(date)
        time_correspondence_file =  vid_start_end + sbj_id + "_" + str(date) + ".p"
        cluster_file = ecog_cluster_loc + sbj_id + "_" + str(date) + ".p"
        check_labels.label_histogram_cluster(sbj_id, date, extracted_label_loc, int(level),
                                             best_corr_clusters[d], cluster_file,
                                             time_correspondence_file, label_accuracy_loc + level + "_")
    #Back project cluster center
    for d, date in enumerate(dates):
        print "Starting: Back projecting for day " + str(date)
        pca_model = ecog_feature_loc + "transformed_pca_model_" + sbj_id + "_" + str(date) + ".p"
        cluster_center_file = ecog_cluster_loc + sbj_id + "_" + str(date) + "_" + level + "_centers.p"
        back_project(pca_model, cluster_center_file,
                     best_corr_clusters[d], back_project_loc + sbj_id + "_" + str(date) + "_" + level + "_")

    #Summary statistics

    #Normal
    print sbj_id
    total_recall = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
    total_precision = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
    total_f1 = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
    tracks = ["Mvmt", "Sound", "Rest", "Other"]
    for file in glob.glob((label_accuracy_loc) + "\\" + level + "_" + "*_results.p"):

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
    for file in glob.glob((label_accuracy_loc) +  "\\" + level + "_" + "*_results_random.p"):
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

    print "------------------------Percentile of score in RANDOM------------------------------------"

    total_f1_percentile = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
    for file in glob.glob((label_accuracy_loc) +  "\\" + level + "_" + "*_results_random.p"):
        filename = file.split("\\")[-1]
        filenum = filename.split("_")[1]
        date = filename.split("_")[2]
        summaries = pickle.load(open(label_accuracy_loc + "\\"
                                     + level +"_" + filenum + "_" + date + "_results.p", "rb"))
        summaries_random = pickle.load(open(file, "rb"))
        for s, summary in enumerate(summaries):
            ind = summary["track"]
            if summary['f1_score']==-1:
                total_f1_percentile[ind].append(-1)
            else:
                percentile = percentileofscore(summaries_random[s]['f1_score'],summary['f1_score'])
                total_f1_percentile[ind].append(percentile)
    pickle.dump(total_f1_percentile, open(label_accuracy_loc + "percentile_" + level + ".p", "wb"))
    percentile_save_file.writerow([sbj_id])
    for key, val in total_f1_percentile.items():
        percentile_save_file.writerow([key, val])
    print sbj_id
    print "f1"
    print_averages(total_f1_percentile)
    print total_f1_percentile

#Summary statistics

#Normal
total_recall = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
total_precision = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
total_f1 = {"Mvmt":[], "Sound":[], "Rest":[], "Other":[]}
tracks = ["Mvmt", "Sound", "Rest", "Other"]
for file in glob.glob(os.path.dirname(os.path.dirname(label_accuracy_loc))
                              + "\\*" + "\\" + level + "_" + "*_results.p"):

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
for file in glob.glob(os.path.dirname(os.path.dirname(label_accuracy_loc))
                              + "\\*" + "\\" + level + "_" + "*_results_random.p"):
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