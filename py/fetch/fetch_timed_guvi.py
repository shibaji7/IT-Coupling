#!/usr/bin/env python

"""fetch_timed_guvi.py: module is dedicated to fetch GUVI data."""

__author__ = "Chakraborty, S."
__copyright__ = ""
__credits__ = []
__license__ = "MIT"
__version__ = "1.0."
__maintainer__ = "Chakraborty, S."
__email__ = "shibaji7@vt.edu"
__status__ = "Research"

import os
import datetime as dt
import glob
from scipy.io import readsav

class GUVITS(object):
    """
    This class is dedicated to extract GUVI data from a folder
    located at the local repository.
    """

    def __init__(self, base, dates):
        """
        Parameters:
        -----------
        base: Base folder to store data
        dates: Start and end dates
        """
        self.dates = dates
        self.base = base
        os.makedirs(base, exist_ok=True)
        self.__loadSAV__()
        return

    def __loadSAV__(self):
        """
        Load sav data from folder
        """
        files = glob.glob(self.base + "*.sav")
        for f in files:
            o = readsav(f)
            secs = [x.sec for x in o["ndpsorbit"]]
            glat, glon = [x.glat for x in o["ndpsorbit"]], [x.glong for x in o["ndpsorbit"]]
            sza, ap = [x.sza for x in o["ndpsorbit"]], [x.ap for x in o["ndpsorbit"]]
            print(glat, glon, sza)
            break
        return

    @staticmethod
    def fetch(base, dates):
        return GUVITS(base, dates)

if __name__ =="__main__":
    GUVITS.fetch(
        "data/2005-09-07-17-40/",
        [
            dt.datetime(2005, 9, 7, 17), 
            dt.datetime(2005, 9, 7, 20),
        ],
    )