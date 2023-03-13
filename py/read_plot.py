
import matplotlib.pyplot as plt
plt.style.use(['science','ieee'])

import glob
from scipy.io import readsav
import datetime as dt
import pandas as pd


files = glob.glob("data/*.sav")
files.sort()

dates = []
zm, sza = [], []
T, O, O2, N2 = [], [], [], []
glat, glong = [], []
errT, errO, errO2, errN2 = [], [], [], []
for t in files:
    sav = readsav(t).ndpsorbit
    for rec in sav:
        dates.append(
            dt.datetime(2003,1,1)+
            dt.timedelta(float(rec.iyd)-1)+
            dt.timedelta(seconds=float(rec.sec))
        )
        glat.append(rec.glat)
        glong.append(rec.glong)
        zm.append(rec.zm)
        T.append(rec.t)
        O.append(rec.ox)
        O2.append(rec.o2)
        N2.append(rec.n2)
        errT.append(rec.sigt)
        sza.append(rec.sza)
o = pd.DataFrame()
o["time"], o["zm"] = dates, zm
o["t"], o["sigt"], o["sza"] = T, errT, sza
o["o2"], o["o"], o["n2"] = O2, O, N2
o["glat"], o["glong"] = glat, glong
o = o.sort_values(by="time")
o = o[o.time>dt.datetime(2003,11,4,19)]
print(o.head())
    
i, j = 0, 110
print(o.iloc[i].time,o.iloc[i].glat, o.iloc[i].glong, o.iloc[i].sza)
print(o.iloc[j].time,o.iloc[j].glat, o.iloc[j].glong, o.iloc[j].sza)

fig = plt.figure(dpi=240, figsize=(5, 2.5))
ax = fig.add_subplot(121)
ax.errorbar(o.iloc[i].t, o.iloc[i].zm, xerr=o.iloc[i].sigt, 
    capsize=0.1, color="k", ls="None", fmt="o", ms="0.6", lw=0.4, label="19 UT")
ax.errorbar(o.iloc[j].t, o.iloc[j].zm, xerr=o.iloc[j].sigt, 
    capsize=0.1, color="r", ls="None", fmt="o", ms="0.6", lw=0.4, label="20 UT")
ax.set_ylabel("Height, km")
ax.set_xlabel("Temperature, K")
ax.set_xlim(100, 1500)
ax.set_ylim(100, 600)
ax.legend(loc=2)


ax = fig.add_subplot(122)
ax.set_xlabel("Density, $cm^{-3}$")
ax.set_ylim(100, 600)
ax.semilogx(o.iloc[i].o, o.iloc[i].zm, color="k", ls="-", label="O")
ax.semilogx(o.iloc[i].n2, o.iloc[i].zm, color="k", ls=":", label=r"$N_2$")
ax.semilogx(o.iloc[i].o2, o.iloc[i].zm, color="k", ls="--", label=r"$O_2$")

ax.semilogx(o.iloc[j].o, o.iloc[j].zm, color="r", ls="-")
ax.semilogx(o.iloc[j].n2, o.iloc[j].zm, color="r", ls=":")
ax.semilogx(o.iloc[j].o2, o.iloc[j].zm, color="r", ls="--")
ax.set_yticklabels(["", "", "","","",""])
ax.legend(loc=3)

fig.subplots_adjust(wspace=0.1, hspace=0.1)
fig.savefig("Cashes.png", bbox_inches="tight")