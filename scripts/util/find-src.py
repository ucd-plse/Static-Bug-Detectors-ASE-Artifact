''' 
Finds directory containing source files.
Writes the directory pathname to path.txt
'''

import os

for root, dirs, files in os.walk('/root/home'):
    for name in files:
        if 'README.md' in name:
            f = open('/root/home/path.txt', 'w')
            f.write(root)
            break
