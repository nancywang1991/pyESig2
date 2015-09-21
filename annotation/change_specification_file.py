import glob
import pdb
import io
import codecs
import xml.etree.ElementTree as ET

file_dir = "C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\" + \
           "manual_annotations\\labels\\"

files = glob.glob(file_dir + "*\\*\\*.anvil")

for file in files:
    lines = []
    #doc = ET.parse(file)
    #root = doc.getroot()
    #pdb.set_trace()
    with codecs.open(file, "r", encoding='utf-16') as infile:
        cnt = 0
        for line in infile:
            if cnt == 3:
                lines.append("    <specification src=\"../../specifications.xml\" />\r\n")
            else:
                lines.append(line)
            cnt += 1
    with codecs.open(file, "w", encoding='utf-16') as outfile:
        for line in lines:
            outfile.write(line)


