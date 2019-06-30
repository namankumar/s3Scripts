# Dump an S3 bucket to local drive fast and reliably

This code builds on top of the others' work that I found via random Google searches.

## Motivation
* wanted to parallelize downloading files. Currently availale utility, like s3cmd, download one file at a time
* wanted a super simple interface to download an entire bucket
* finer grain control over what / how the code actually does

## How to use this
* download.py downloads an entire s3 bucket to local drive
* inputs: bucket name, local path, number of threads
* the more the number of threads, the more simultanuous files you can download. Three is a good number of threads but you may want to experiment for your internet connection
* on error, it'll just continue to download rest of the bucket
* after it finishes, you'll need to account for two edge cases: files not downloaded due to brief connection loss, files partially downloaded
* first case can be handled by just running the script agin. It will update missing files without overwriting existing files
* for second case, run checkmd5.py and delete all the files that do not match. Copy paste the list into del.txt and run 'cat del.txt | xargs rm'
* run download.py again!
* your entire bucket should be mirrored on your local drive in significantly less time than pretty much any other utility, including s3cmd!
