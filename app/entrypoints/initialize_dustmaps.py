import dustmaps.sfd
from dustmaps.config import config
from django.conf import settings
import os

media_root = settings.MEDIA_ROOT
config.reset()

config["data_dir"] = f"{media_root}/../dustmaps"

# Download data if is missing
for data_file in [
    f'''{config["data_dir"]}/sfd/SFD_dust_4096_ngp.fits''',
    f'''{config["data_dir"]}/sfd/SFD_dust_4096_sgp.fits''',
]:
    if not os.path.exists(data_file):
        dustmaps.sfd.fetch()
        break

# Create dustmap config file if it is missing
dustmap_config = f"{os.environ['HOME']}/.dustmapsrc"
if not os.path.exists(dustmap_config):
    with open(dustmap_config, 'w') as fout:
        print(f'''{{"data_dir": "{config["data_dir"]}"}}''', file=fout)
