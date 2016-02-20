__author__ = 'wangnxr'
import xmltodict
import xml.etree.ElementTree as ET
import numpy as np
import glob
from PIL import Image
import lxml.etree as etree
import os

def label_parse(fname):
    with open(fname) as fd:
        doc = xmltodict.parse(fd.read())
        if doc["annotation"]["keypoints"] is None:
            return -1, -1, -1, -1
        xmin = np.inf
        xmax = -np.inf
        ymin = np.inf
        ymax = -np.inf
        for i in xrange(len(doc["annotation"]["keypoints"]["keypoint"])):
            cur_keypoint = doc["annotation"]["keypoints"]["keypoint"][i]
            xmin = min(xmin, int(float(cur_keypoint["@x"]))-20)
            ymin = min(ymin, int(float(cur_keypoint["@y"]))-20)
            xmax = max(xmax, int(float(cur_keypoint["@x"]))+20)
            ymax = max(ymax, int(float(cur_keypoint["@y"]))+20)
            if cur_keypoint["@name"] == "Nose":
                ymin = min(ymin, int(float(cur_keypoint["@y"]))-70)
                ymax = min(ymin, int(float(cur_keypoint["@y"]))+270)
    return xmin, ymin, xmax, ymax



label_dir = "D:\\keyframes\\fcb01f7a\\"
if not os.path.isdir(label_dir + "Annotations"):
    os.makedirs(label_dir + "Annotations")

for fname in glob.glob(label_dir + "\\info\\*"):
    xmin, ymin, xmax, ymax = label_parse(fname)
    if not (xmin == -1):
        basename = "_".join(fname.split("\\")[-1].split("_")[:3])
        img = Image.open(label_dir + "\\images\\" + basename + ".jpg")
        (image_width, image_height) = img.size

        root = ET.Element("annotation")
        ET.SubElement(root, "folder").text = "PatientVids"
        ET.SubElement(root, "filename").text = basename + ".jpg"
        size = ET.SubElement(root, "size")
        ET.SubElement(size, "width").text = str(image_width)
        ET.SubElement(size, "height").text = str(image_height)
        ET.SubElement(size, "depth").text = "3"
        ET.SubElement(root, "segmented").text = "0"
        obj=ET.SubElement(root, "object")
        ET.SubElement(obj, "name").text = "patient"
        ET.SubElement(obj, "pose").text = "Unspecified"
        ET.SubElement(obj, "truncated").text = "1"
        ET.SubElement(obj, "difficult").text = "0"
        box = ET.SubElement(obj, "bndbox")
        ET.SubElement(box, "xmin").text = str(xmin)
        ET.SubElement(box, "ymin").text = str(ymin)
        ET.SubElement(box, "xmax").text = str(xmax)
        ET.SubElement(box, "ymax").text = str(ymax)

        tree = ET.ElementTree(root)
        save_name = label_dir + "\\Annotations\\" + basename + ".xml"
        tree.write(save_name)
        x = etree.parse(save_name)
        save_file = open(save_name, "wb")
        save_file.write(etree.tostring(x, pretty_print=True))