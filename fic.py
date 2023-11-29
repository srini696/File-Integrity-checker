import os
import hashlib
import smtplib
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Define the list of directories to monitor

DIRECTORIES = ['/usr']

# Directory to store baseline data

BASELINE_DIR = '/home/sbiyagu/project/baseline'


def compute_checksum(file_path):
  '''
    calculates SHA-512 checksum for a file
  '''
  sha512 = hashlib.sha512()
  with open(file_path, 'rb') as f:
    while True:
      data = f.read(65536)
      if not data:
        break
      sha512.update(data)
  return sha512.hexdigest()


def validate_checksums():
  '''
    compares checksums and detect changes
  '''
  changes_detected = [[False,'',[]]]*len(DIRECTORIES)
  dir_id=-1
  for directory in DIRECTORIES:
    dir_id+=1
    print(f'Current directory being monitored :{directory}.....')
    print(f'Iterating through the whole directory tree.....') 
    with open(os.path.join(BASELINE_DIR, directory.strip('/')) + '.txt', 'r') as baseline_file:
      baseline_list  = [line.split() for line in baseline_file.read().splitlines()]
      baseline_filtered =[]
      for ele in baseline_list:
          if len(ele)!=2:
              baseline_filtered.append([ele[0],ele[-1]])
          else:
              baseline_filtered.append(ele)
      baseline_data = dict(baseline_filtered)
      print(f'Extracting baseline data from initial hashed files.....')
    current_files=[]
    new_files=[]
    print(f'Comparing hashed values of current files in the directory with baseline data.....')
    for root, fpath, files in os.walk(directory):
      for file in files:
        file_path = os.path.join(root, file)
        if len(file_path.split())!=1 or os.path.islink(file_path) or os.stat(file_path).st_nlink>1:
            continue
        new_files.append(file_path)
        if file_path in baseline_data:
          current_checksum = compute_checksum(file_path)
          current_files.append(file_path)
          if current_checksum != baseline_data[file_path]:
            logging.warning(f'Changes detected in {file_path}')
            changes_detected[dir_id][0] = True
            changes_detected[dir_id][1]+='U'
            changes_detected[dir_id][2].append(file_path)
        else:
            logging.warning(f'New file added in {file_path}')
            changes_detected[dir_id][0] = True
            changes_detected[dir_id][1]+='A'
            changes_detected[dir_id][2].append(file_path)
  return changes_detected


def alert_sys_admin(subject, message):
  '''
    send email notification to system administrator that file is modified 
  '''
  sender_email = 'sbiyagu@g.clemson.edu'
  receiver_email = 'testing.email123linux@gmail.com'
  password = 'sbiyagu1998@'
  msg = MIMEMultipart()
  msg['From'] = sender_email
  msg['To'] = receiver_email
  msg['Subject'] = subject
  msg.attach(MIMEText(message, 'plain'))
  try:
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
      server.ehlo()
      server.starttls()
      server.login(sender_email, password)
      server.sendmail(sender_email, receiver_email, msg.as_string())
      server.close()
    logging.info('Email alert sent.\n')
  except Exception as e:
    logging.error(f'Failed to send email alert: {e}')



def file_integrity_check():
  '''
    check integrity of files on regular basis
  '''
  validation_results = validate_checksums()
  flag=0
  for result in validation_results:
    if result[0]:
      if result[1]=='U':
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.info(f'Integrity check at {timestamp} - Changes detected.\n')
        body='Changes were detected in the following monitored files:\n'+str(result[2])+'\n'
        alert_sys_admin('File Integrity Check Alert', body)
        print(f'Changes were detected in monitored directories!!!')
      else:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.info(f'Integrity check at {timestamp} - Changes detected.\n')
        body='Files were added in the following file paths:\n'+str(result[2])+'\n'
        alert_sys_admin('File Integrity Check Alert', body)
        print(f'Files were added in monitored directories!!!')      
    else:
      flag=1 
  if flag==1: 
    print(f'File integrity check is successfully completed and integrity is maintained\n')

# Function to initialize logging

def initialize_logger():
  '''
    Initializes logger to log them into integrity_checker.log
  '''
  logging.basicConfig(filename='integrity_checker.log', level=logging.INFO, format='%(asctime)s - %(message)s')


if __name__ == '__main__':
  '''
    Driver code
  '''
  initialize_logger()
  file_integrity_check()

