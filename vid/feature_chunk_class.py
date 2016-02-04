import cPickle as pickle
import pdb
import os
class feature_chunk:
    def __init__(self, file_loc, sbj_id, day_num):
        self.file_loc = file_loc
        self.sbj_id = sbj_id
        self.day_num = day_num
        self.cur_file_num = 0
        #pdb.set_trace()
        self.cur_feature_chunk = pickle.load(open(self.file_loc + "\\" + sbj_id + "_" + str(day_num) \
                                + "_" + format(self.cur_file_num, '04') + ".p", 'rb'))
        
        self.cur_feature_chunk_len = len(self.cur_feature_chunk)
        self.cur_frame = 0
        self.cur_file_num += 1
        self.total_frame = 0
        
        
        
    def load_new_file(self):
        self.cur_feature_chunk = pickle.load(open(self.file_loc + "\\" + self.sbj_id + "_" + str(self.day_num) \
                                + "_" + format(self.cur_file_num, '04') + ".p", 'rb'))

        self.cur_feature_chunk_len = len(self.cur_feature_chunk)
        self.cur_frame = 0
        self.cur_file_num += 1

    def has_next(self):
        if self.cur_frame >= self.cur_feature_chunk_len:
            return os.path.isfile(self.file_loc + "\\" + self.sbj_id + "_" + str(self.day_num) \
                                + "_" + format(self.cur_file_num , '04') + ".p")
        else: return True
    
    def next(self):
        if self.cur_frame >= self.cur_feature_chunk_len:
            #print self.cur_feature_chunk_len
            #if self.cur_feature_chunk_len/30<100:
            #    pdb.set_trace()
            self.load_new_file()

        feature_chunk_val = self.cur_feature_chunk[self.cur_frame]
        self.cur_frame += 1
        self.total_frame +=1

        return feature_chunk_val

    def rewind(self):
        self.cur_feature_chunk = None
        self.cur_feature_chunk_len = 0
        self.cur_file_num = 0
        self.load_new_file()
        self.cur_frame = 0
        
