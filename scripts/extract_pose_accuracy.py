from __future__ import print_function
__author__ = 'wangnxr'

import pdb

fname = "C:\\Users\\wangnxr\\Downloads\\deeppose\\scripts\\test_400\\test_400.log"
outfile = "C:\\Users\\wangnxr\\Downloads\\deeppose\\scripts\\test_400\\test_400_summary.txt"

cur_movie = ""
result_stats = [{"name":"","avg":0,"max":0,"min":100, "cnt":-1}]

with open(fname, "rb") as infile:
    for line in infile.readlines():
            movie_name = "-".join(line.split(" ")[-1].split("\t")[0].split("/")[-1].split("-")[:-1])
            if movie_name == "":
                movie_name = line.split(" ")[-1].split("\t")[0].split("/")[-1].split("_")[0]
            if not movie_name == result_stats[-1]["name"]:
                result_stats[-1]["avg"] /=  result_stats[-1]["cnt"]
                result_stats.append({"name":movie_name, "avg":0, "min":100, "max":0, "cnt": 0})
            error = float(line.split("\t")[1].split(":")[-1])
            result_stats[-1]["avg"] += error
            result_stats[-1]["cnt"] += 1
            if error < result_stats[-1]["min"]:
                result_stats[-1]["min"]=error
            if error > result_stats[-1]["max"]:
                result_stats[-1]["max"]=error
result_stats[-1]["avg"] /=  result_stats[-1]["cnt"]
with open(outfile, "wb") as out:
    for res in result_stats:
        print("name: " + res["name"] + " avg: " + str(res["avg"]) + " max: " + str(res["max"])
        + " min: " + str(res["min"]) + " cnt: " + str(res["cnt"]), file=out)