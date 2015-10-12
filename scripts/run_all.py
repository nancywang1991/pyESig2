__author__ = 'wangnxr'

from pyESig2.cluster import truncated_hier_cluster
from pyESig2.vid import aggregate
from pyESig2.validation import check_labels
from pyESig2.analysis import correlate_signals
from pyESig2.annotation import extract_labels
from pyESig2.vid.misc_funcs import has_video

#Raw_sources
level = '4'
#sbj_id="e70923c4"
sbj_id="fcb01f7a"
#sbj_id="a86a4375"
#sbj_id="c95c1e82"
#dates=[4,5,7]
#dates=[8,10,11,12]
#dates=[4,5]
#dates=[4,5,7]
dates=[16]
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
    best_corr_clusters.append(correlate_signals.correlate(mvmt_loc + sbj_id + "_" + str(date) + ".p",
                                sound_loc  + str(date) + "\\" + sbj_id + "_" + str(date) + ".p",
                                 ecog_cluster_loc + sbj_id + "_" + str(date) + "_" + level + ".p"))
#Extract labels
for date in dates:
    print "Starting: Extracting labels for day " + str(date)
    extract_labels.extract_reduced_labels(sbj_id, date, label_loc, video_loc, extracted_label_loc)
    extract_labels.extract_random_labels(sbj_id, date, label_loc,
                                          video_loc, extracted_random_label_loc)

#Check labels
for date in dates:
    print "Starting: Checking labels for day " + str(date)
    time_correspondence_file = vid_start_end + sbj_id + "_" + str(date) + ".p"
    condensed_cluster_file = ecog_cluster_loc + sbj_id + "_" + str(date) + "_" + level + ".p"
    check_labels.label_accuracy(sbj_id, date, extracted_label_loc, extracted_random_label_loc,
                   condensed_cluster_file, time_correspondence_file, label_accuracy_loc)
    check_labels.cluster_label_accuracy(sbj_id, date, best_corr_clusters[dates.index(date)],
                                extracted_label_loc, extracted_random_label_loc,
                                condensed_cluster_file, time_correspondence_file, label_accuracy_loc)
#Label_histograms
for date in dates:
    print "Starting: Generating histograms for day " + str(date)
    time_correspondence_file =  vid_start_end + sbj_id + "_" + str(date) + ".p"
    cluster_file = ecog_cluster_loc + sbj_id + "_" + str(date) + ".p"
    check_labels.label_histogram(sbj_id, date, extracted_label_loc,
                                 cluster_file, time_correspondence_file, label_accuracy_loc)
