#!/usr/bin/env python

"""get_sol.py: module is dedicated to fetch solar irradiance data."""

__author__ = "Chakraborty, S."
__copyright__ = ""
__credits__ = []
__license__ = "MIT"
__version__ = "1.0."
__maintainer__ = "Chakraborty, S."
__email__ = "shibaji7@vt.edu"
__status__ = "Research"

import calendar
import datetime as dt
import os

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import netCDF4 as nc
import numpy as np
import pandas as pd
import requests
from netCDF4 import Dataset
from loguru import logger

from sunpy import timeseries as ts
from sunpy.net import Fido
from sunpy.net import attrs as a


class FlareTS(object):
    """
    This class is dedicated to plot GOES, RHESSI, and SDO data
    from the repo using SunPy
    """

    def __init__(self, ev, dates):
        """
        Parameters
        ----------
        ev: Event datetime
        dates: list of datetime object for start and end of TS
        """
        self.ev = ev
        self.base = f"data/{ev.strftime('%Y-%m-%d-%H-%M')}/"
        self.dates = dates
        self.dfs = {}
        os.makedirs(self.base, exist_ok=True)
        if self.ev.year >= 2009: self.__loadGOESX__()
        else: self.__loadGOES__()
        self.__loadRHESSI__()
        self.__loadEUVs__()
        return

    def __key_map__(self, sat):
        """
        Get keys for netcdf files
        """
        _map_ = {
            "15": ["A_AVG", "B_AVG"],
            "12": ["xs", "xl"],
        }
        return _map_[str(sat)]

    def __loadGOES__(self, sat=12):
        fn = self.base + "GOES.csv"
        if not os.path.exists(fn):
            o = pd.DataFrame()
            date = self.dates[0]
            _, d0 = calendar.monthrange(date.year, date.month)
            fname = "g{s}_xrs_1m_{y}{m}{d}_{y}{m}{d0}.nc".format(
                s=sat,
                y=date.year,
                m="%02d" % date.month,
                d="%02d" % 1,
                d0=d0,
            )
            uri = "https://satdat.ngdc.noaa.gov/sem/goes/data/avg/{y}/{m}/goes{s}/netcdf/".format(
                s=sat,
                y=date.year,
                m="%02d" % date.month,
            )
            url = uri + fname
            logger.info(f"File {url}")
            fname = self.base + fname
            os.system(f"wget -O {fname} {url}")
            ds = nc.Dataset(fname)
            keys = self.__key_map__(sat)
            o["hxr"], o["sxr"] = ds.variables[keys[0]][:], ds.variables[keys[1]][:]
            tunit, tcal = (
                ds.variables["time_tag"].units,
                ds.variables["time_tag"].calendar,
            )
            o["tval"] = nc.num2date(
                ds.variables["time_tag"][:], units=tunit, calendar=tcal
            )
            ds.close()
            o = o[(o.tval >= self.dates[0]) & (o.tval <= self.dates[1])]
            o.to_csv(fn, index=False, header=True, float_format="%g")
            os.remove(fname)
        else:
            logger.info(f"Local file {fn}")
            self.dfs["goes"] = pd.read_csv(fn, parse_dates=["tval"])
        return

    def __loadGOESX__(self):
        """
        Load GOES data from remote/local repository
        """
        self.dfs["goes"], self.goes = pd.DataFrame(), []
        result = Fido.search(a.Time(self.dates[0], self.dates[1]), a.Instrument("XRS"))
        if len(result) > 0:
            logger.info(f"Fetched GOES: \n {result}")
            tmpfiles = Fido.fetch(result)
            for tf in tmpfiles:
                self.goes.append(ts.TimeSeries(tf))
                self.dfs["goes"] = pd.concat(
                    [self.dfs["goes"], self.goes[-1].to_dataframe()]
                )
            self.dfs["goes"].index.name = "time"
            self.dfs["goes"] = self.dfs["goes"].reset_index()
        logger.info(f"Data from GOES XRS: \n {self.dfs['goes'].head()}")
        return

    def __loadRHESSI__(self):
        """
        Load RHESSI data from remote/local repository
        """
        self.rhessi, self.dfs["rhessi"] = [], pd.DataFrame()
        result = Fido.search(
            a.Time(self.dates[0], self.dates[1]), a.Instrument("RHESSI")
        )
        if len(result) > 0:
            logger.info(f"Fetched RHESSI: \n {result}")
            tmpfiles = Fido.fetch(result)
            for tf in tmpfiles:
                if "obssum" in tf:
                    self.rhessi.append(ts.TimeSeries(tf))
                    self.dfs["rhessi"] = pd.concat(
                        [self.dfs["rhessi"], self.rhessi[-1].to_dataframe()]
                    )
            self.dfs["rhessi"].index.name = "time"
            self.dfs["rhessi"] = self.dfs["rhessi"].reset_index()
        logger.info(f"Data from RHESSI XRS: \n {self.dfs['rhessi'].head()}")
        return

    def __loadSEE__(self):
        """
        Load SEE data Level 3A for flare info
        """
        fname = ""
        baseURL = "http://lasp.colorado.edu/data/timed_see/level3a/{Y}/"
        return

    def __loadEUVs__(self):
        # SOHO SEM Data, download to sunpy data dircetory
        from soho_loader import soho_load
        df, _ = soho_load(dataset="SOHO_CELIAS-SEM_15S",
                     startdate=self.dates[0],
                     enddate=self.dates[1],
                     path=None,
                     resample=None,
                     pos_timestamp=None,
                     max_conn=5)
        self.dfs["soho"] = df
        # XPS 5-min data
        zipFname = "sorce_xps_L4_c05m_r0.1nm_{Y}.ncdf.zip".format(
            Y=self.dates[0].year
        )
        unzipFname = "sorce_xps_L4_c05m_r0.1nm_{Y}.ncdf".format(
            Y=self.dates[0].year
        )
        if not os.path.exists(unzipFname):
            link = "http://lasp.colorado.edu/data/sorce/ssi_data/xps/level4/5min/"
            os.system(f"wget {link}{zipFname} -O {zipFname}")
            import zipfile
            with zipfile.ZipFile(zipFname, "r") as zip:
                zip.extractall(f"./{unzipFname}")
            os.remove(zipFname)
        return

    def plot_TS_dataset(
        self,
        ax=None,
        ylim=[1e-8, 1e-3],
        comps={
            "hxr": {"color": "b", "ls": "None", "lw": 0.5},
            "sxr": {"color": "r", "ls": "None", "lw": 0.5},
        },
        high_res=False,
        xlabel="UT",
        ylabel=r"$I_{\infty}^{GOES}$, $Wm^{-2}$",
        loc=2,
        fname=None,
    ):
        """
        Overlay station data into axes
        """
        plt.style.use(["science", "ieee"])
        if ax is None:
            fig = plt.figure(dpi=180, figsize=(5, 3))
            ax = fig.add_subplot(111)
        else:
            fig = plt.gcf()
        data = self.high_res_data if high_res else self.low_res_data
        if ylim:
            ax.set_ylim(ylim)
        ax.xaxis.set_major_formatter(mdates.DateFormatter(r"%H^{%M}"))
        ax.set_xlim(self.dates)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        for comp in comps.keys():
            co = comps[comp]
            ax.semilogy(
                data.tval,
                data[comp],
                marker=".",
                ls=co["ls"],
                color=co["color"],
                lw=co["lw"],
                ms=0.2,
                alpha=0.9,
                label=comp.upper(),
            )
        ax.set_ylim(1e-8, 1e-2)
        ax.legend(loc=loc, fontsize=6)
        if fname:
            fig.savefig(fname, bbox_inches="tight")
        return fig, ax


# Test codes
if __name__ == "__main__":
    FlareTS(
        dt.datetime(2005, 9, 7, 17, 40),
        [
            dt.datetime(2005, 9, 7, 17), 
            dt.datetime(2005, 9, 7, 18)
        ]
    )