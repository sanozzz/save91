import csv, numpy as np, online_plan as op
rows = list(csv.DictReader(open("tables/ltv_mc_draws.csv"))); v = lambda k: np.array([float(r[k]) for r in rows])
print("door pay<=24", (v("door_pay")<=24).mean(), " online 8y >=3", (v("on_ltv96")>=3).mean(), " door >=3", (v("door_ltv60")>=3).mean())
x = op.saver_inputs(); p = op.profiles(x)
print("deposits 60m", round(p["deposits"][0][:60].sum()), "s at m60 (index 59, 60)", round(p["still_saving"][0][59],3), round(p["still_saving"][0][60],3))
print("balance per saver won m96 (avg in month)", round(p["balance"][0][95]))
xd = op.saver_inputs(doorstep=True); pd = op.profiles(xd); print("door balance m96", round(pd["balance"][0][95]), "door s60", round(pd["still_saving"][0][59],3))
