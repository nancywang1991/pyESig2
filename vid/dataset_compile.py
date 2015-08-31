import numpy as np
import csv
import glob
import os
import shutil
import pdb

annotation_loc = "C://Users//wangnxr//Documents//rao_lab" + \
                     "//video_analysis//manual_annotations//sleep.csv"
face_loc = "D://face//"
ecog_loc = "D://face_ecog//"
result_loc = "D://face_ecog_dataset2//"
cnt = 0
with open(annotation_loc, 'rb') as csvfile:
    with open(result_loc + 'labels.csv', 'wb') as writefile:
        sleepreader = csv.reader(csvfile, dialect = 'excel')
        sleepreader.next()
        sleepwriter = csv.writer(writefile)
        sleepwriter.writerow(['video_num', 'sleep?'])
        for row in sleepreader:
            
            if row[0]=="a86a4375" and row[1] == '2' and int(row[3]) < 2:
                
                files = glob.glob(face_loc + row[0] + "_" + str(row[1]) + "//" + \
                          str(row[2]).zfill(4) + "*_1.png")
                for f in files:
                    dirname,fname = f.split("\\")
                    name, ext = fname.split(".")
                    vid, num, frame = name.split("_")
                    ecog_file = ecog_loc + row[0] + "_" + row[1] + "//" + \
                                str(int(vid))+ "_" + num + ".p"
                    if (os.path.exists(ecog_file)):
                        if row[3] == '0':
                            shutil.copy(f, result_loc + "face//" + str(cnt) + ".png")
##                            shutil.copy(f[:-5] + "2.png", result_loc + "face//" + str(cnt) + "_1.png")
##                            shutil.copy(f[:-5] + "3.png", result_loc + "face//" + str(cnt) + "_2.png")
##                            shutil.copy(f[:-5] + "4.png", result_loc + "face//" + str(cnt) + "_3.png")
                            shutil.copy(ecog_file,
                                        result_loc + "ecog//" + str(cnt) + ".p")
                            sleepwriter.writerow([str(cnt), row[6]])
##                        elif row[3] == '1':
##                            if abs(int(num) - int(row[4]))<5:
##                                sleepwriter.writerow([str(cnt), int(row[6])+2])
##                            elif int(num) > int(row[4]):
##                                sleepwriter.writerow([str(cnt), abs(int(row[6])-1)])
##                            else:
##                                sleepwriter.writerow([str(cnt), int(row[6])])
##                        else:
##                            if abs(int(num) - int(row[4]))<5 or abs(int(num) - int(row[5]))<5:
##                                sleepwriter.writerow([str(cnt), int(row[6])]+2)
##                            elif int(num) < int(row[4]):
##                                sleepwriter.writerow([str(cnt), int(row[6])])
##                            elif int(num) < int(row[5]):
##                                sleepwriter.writerow([str(cnt), abs(int(row[6])-1)])
##                            else:
##                                sleepwriter.writerow([str(cnt), int(row[6])])
                            cnt += 1
                        
            
                    
                
                    
                
        

