import os
import glob

folder_loc = "D:\\NancyStudyData\\raw\\86a4375a\\86a4375a_2\\"
orig_name = "Timm~ Katrina_497a1ff8-9b6f-4868-bd2d-752c6b86e192"

for f in glob.glob(folder_loc + "*"):
    parent, base = os.path.split(f)
    grandparent, id = os.path.split(parent)
    new_name = base.replace( id, orig_name)
    os.rename(f, parent + "\\" + new_name)
