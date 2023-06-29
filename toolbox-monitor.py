import re
import os
import shutil
import sys
from urllib import request

TOOLBOX_URL = "https://www.ibm.com/support/pages/aix-toolbox-open-source-software-downloads-alpha"
RPMS_LIST = sys.argv[1] # rpm -qa > rpms.txt
DOWNLOAD_DIR = 'downloads' # Kinda download cache
INSTALL_DIR = 'install' # Output directory for rpm's to be updated

os.makedirs(DOWNLOAD_DIR, exist_ok = True)
os.makedirs(INSTALL_DIR, exist_ok = True)

# Get content of AIX toolbox
req = request.Request(url = TOOLBOX_URL, headers = { 'User-Agent' : 'rpmc1.0' })
content = request.urlopen(req).read().decode('utf-8')

# Cleanup installation directory
for f in os.listdir(INSTALL_DIR):
	os.remove(os.path.join(INSTALL_DIR, f))

# For each installed RPM package 
with open(RPMS_LIST) as f:
	for line in f:
		rpm = re.sub('\.ppc$', '', line.strip())
		rpm = rpm.replace('++','plusplus')
		if not rpm in content:	# There is no installed version on the site
			upd = '-'
			try:	# Find latest version
				m = re.match(r'^(.+)-([\w\.]+)-\w+$', rpm)
				if m:
					pkg = m.group(1)
					pp = f'https://.*/{pkg}-\d.*\.ppc\.rpm'
					n = re.search(pp, content, re.M)	# re.M means multiline
					if n:
						url = n.group(0)
						upd = url.split('/')[-1]
						file = os.path.join(DOWNLOAD_DIR, upd)
						if not os.path.isfile(file):	# Download file if it was not done before
							request.urlretrieve(url, file)
						shutil.copy(file, INSTALL_DIR)	# Copy file to install dir
			except re.error:
				file = '?'
			print(rpm, '--->', upd)

shutil.make_archive(RPMS_LIST.replace('.txt',''),'zip','install')