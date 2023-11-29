import os
import hashlib

DIRECTORIES = ['/usr']

# Directory to store baseline data

BASELINE_DIR = '/home/sbiyagu/project/baseline'


def compute_hash(file_path):
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


def initiate_original_baseline():
  '''
    creates the initial baseline
  '''
  if not os.path.exists(BASELINE_DIR):
    os.mkdir(BASELINE_DIR,0o666)
  for directory in DIRECTORIES:
    baseline_data = {}
    for root, fpath, files in os.walk(directory):
      for file in files:
        file_path = os.path.join(root, file)
        if os.path.islink(file_path) or os.stat(file_path).st_nlink>1:
            continue
        print(root,file,file_path)
        hash_value = compute_hash(file_path)
        baseline_data[file_path] = hash_value
    with open(os.path.join(BASELINE_DIR, directory.strip('/')) + '.txt', 'w') as baseline_file:
      for file_path, hash_values in baseline_data.items():
        baseline_file.write(f'{file_path} {hash_values}\n')

initiate_original_baseline()
