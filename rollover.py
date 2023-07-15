import os 
import sys 
import datetime

file_path = sys.argv[1]
backup_count = int(sys.argv[2])

#<Summary>
	# Rollover function:
	#   rotates the log file based on the backup_count provided
	#</Summary>
rotated_files = [file_path] + [file_path + '.{}'.format(i) for i in range(1, backup_count + 1)]

if os.path.exists(rotated_files[-1]):
	os.remove(rotated_files[-1])

for i in range(len(rotated_files) - 1, 0, -1):
	source_file = rotated_files[i - 1]
	destination_file = rotated_files[i]
	
	if os.path.exists(source_file):
		os.rename(source_file, destination_file)

open(file_path, 'a').close()