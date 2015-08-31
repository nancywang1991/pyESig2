import os
import glob

folder_loc = "D:\\NancyStudyData\\ecog\\raw\\fcb01f7a\\fcb01f7a_16\\"
#folder_loc = "D:\\NancyStudyData\\eeg\\raw\\ea430431\\ea430431_2\\"
#folder_loc = "E:\\fcb01f7a_16\\"
#orig_name = "Sikes~ Kaitlin_5c0e5194-475e-415b-951b-dbc2e4cc8d18"
orig_name = "Sikes~ Kaitlin_40609f9f-a8d4-4337-84bc-a9e99ed715f6"
#orig_name = "Andrews~ Brian_5add2a18-2d81-4a26-92a9-cfa44f68c583"
#orig_name = "Flack~ Taylor_bd81c1e4-f9c1-41e2-95d8-28568c69f0f1"
#orig_name = "Sikes~ Kaitlin_40609f9f-a8d4-4337-84bc-a9e99ed715f6"
#orig_name = "Moore~ Devon_a06b35a3-d1d3-4794-995f-cad6cfed524e"
for f in glob.glob(folder_loc + "*"):
    parent, base = os.path.split(f)
    grandparent, id = os.path.split(parent)
    new_name = base.replace(orig_name, id)
    #new_name = base.replace( id, orig_name )
    os.rename(f, parent + "\\" + new_name)
