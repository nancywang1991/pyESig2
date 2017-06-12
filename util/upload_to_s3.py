import boto3
import argparse
import glob
from datetime import datetime
import os
import getpass
import subprocess
import botocore

def check_exist(bucketname, filename, s3):
	try:
    		s3.Object(bucketname, filename).load()
	except botocore.exceptions.ClientError as e:
    		if e.response['Error']['Code'] == "404":
        		return False
    		else:
        		raise
	else:
    		return True
def upload_vid(loc, bucketname, s3):
	pass_flag = 0
	while pass_flag == 0:
		password = getpass.getpass()
		password2 = getpass.getpass()
		if not password == password2:
			print "passwords do not match, try again"
		else:
			pass_flag = 1        
	os.chdir(loc)
	files = glob.glob("*/*/*")
	for f, file in enumerate(files):
		if (os.path.isdir(file) or file.split(".")[-1] == "doc" or check_exist(bucketname, file + ".enc", boto3.resource('s3'))):
			continue
		subprocess.call("openssl enc -e -des -in %s -out %s -pass pass:%s" % (file, file + ".enc", password), shell=True)
		if f % 100 == 0:
			print "Uploading %i of %i files" % (f, len(files))
		try:
			s3.upload_file(file + ".enc", bucketname, file + ".enc")
			os.remove(file + ".enc")
		except:
			print file 
	print "Upload complete for location %s at %s" % (loc, str(datetime.now()))

def upload_edf(loc, bucketname, s3):
	os.chdir(loc)
        files = glob.glob("*/*")
        for f, file in enumerate(files):
		if os.path.isdir(file):
			continue
                if f % 100 == 0:
                        print "Uploading %i of %i files" % (f, len(files))
                s3.upload_file(file, bucketname, file)
        print "Upload complete for location %s at %s" % (loc, str(datetime.now()))
	
if __name__=="__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--data_source', required=True, help='source directory to be uploaded, one above the subject ids')
	parser.add_argument('-b', '--bucket_name', required=True)
	parser.add_argument('-t', '--type', required=True, help="Type of data to be uploaded: e=ecog v=video")
	args = parser.parse_args()
	
	s3=boto3.client('s3')
	if args.type=='e':
		print "Uploading ECoG Directory %s" % args.data_source
		upload_edf(args.data_source, args.bucket_name, s3)
	else:
		print "Uploading Video Directory %s" % args.data_source
		upload_vid(args.data_source, args.bucket_name, s3)
