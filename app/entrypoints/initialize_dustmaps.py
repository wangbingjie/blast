import dustmaps.sfd
from dustmaps.config import config
from django.conf import settings
import os

media_root = settings.MEDIA_ROOT
config.reset()

config["data_dir"] = f"{media_root}/../dustmaps/"

if not os.path.exists(
    f"{media_root}/../dustmaps/sfd/SFD_dust_4096_ngp.fits"
) or not os.path.exists(f"{media_root}/../dustmaps/sfd/SFD_dust_4096_sgp.fits"):
    dustmaps.sfd.fetch()