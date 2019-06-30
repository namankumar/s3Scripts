#!/usr/bin/env python


import fnmatch
import os
import boto
import hashlib
from boto.s3.key import Key


SOURCE_DIR  = 'best to use absolute path'
BUCKET_NAME = ''


conn = boto.connect_s3()
bucket = conn.get_bucket(BUCKET_NAME)


def get_md5(filename):
  f = open(filename, 'rb')
  m = hashlib.md5()
  while True:
    data = f.read(10240)
    if len(data) == 0:
        break
    m.update(data)
  return m.hexdigest()

def to_uri(filename):
  return re.sub(SOURCE_DIR, '', f)


#read list of files into a list
#files  = [line.rstrip('\n') for line in open('deletethese.txt')]


#or read files from a folder
files = []
for root, dirnames, filenames in os.walk(SOURCE_DIR):
  for filename in filenames:
     files.append(os.path.join(root, filename))


print('Found {} files to verify', len(files))

# compare them to S3 checksums
files_differ = []
for f in files:
  uri = to_uri(f)
  key = bucket.get_key(uri)
  if key is None:
    files_differ.append(f)
  else:
    md5  = get_md5(f)
    etag = key.etag.strip('"').strip("'")
    if etag != md5:
      print("DIFFERS: "+ f + ": " + md5 + " != " + etag)
      files_differ.append(f)
    else:
      print("verified: "+ f + ": " + md5 + " == " + etag)


print("\n\n\nFILES THAT ARE DIFFERENT")
for f in files_differ:
    print(f)

