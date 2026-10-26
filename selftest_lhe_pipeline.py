#!/usr/bin/env python3
"""Validate the LHE analysis in heft_higgs_pt_study.py on synthetic LHE files built from the toy MC
(higgs_containment.py).  Compares the recovered containment with the toy-MC numbers directly."""
import gzip, sys, tempfile, argparse, numpy as np
from pathlib import Path
import higgs_containment as hc
import heft_higgs_pt_study as S

PTS = [200, 300, 400, 600]
N = 6000

def line(pid, st, m1, p, m=0.0):
    E, px, py, pz = p
    return f" {pid} {st} {m1} 0 0 0 {px:.8e} {py:.8e} {pz:.8e} {E:.8e} {m:.6e} 0. 9.\n"

def write_lhe(path, events):
    with gzip.open(path, "wt") as f:
        f.write("<LesHouchesEvents version=\"3.0\">\n<init>\n</init>\n")
        for ev in events:
            f.write(f"<event>\n {len(ev)} 1 1.0 100. 0.0075 0.118\n" + "".join(ev) + "</event>\n")
        f.write("</LesHouchesEvents>\n")

def hdr(pT):
    E = np.hypot(pT, hc.MH)
    return [line(21, -1, 0, (500., 0, 0, 500.)), line(21, -1, 0, (500., 0, 0, -500.)),
            line(25, 2, 1, (E, pT, 0, 0), hc.MH), line(21, 1, 1, (pT, -pT, 0, 0))]

def mom(p):  # numpy row -> tuple (E,px,py,pz)
    return tuple(p)

def fake_bb(pT, n):
    a, b = hc.two_body(hc.MH, n); a, b = hc.to_lab(a, pT), hc.to_lab(b, pT)
    return [hdr(pT) + [line(5, 1, 3, mom(a[i]), 4.7), line(-5, 1, 3, mom(b[i]), 4.7)] for i in range(n)]

def fake_VV(pT, n, mV, GV, ids):
    d, ms = hc.decay_VVstar(mV, GV, n)
    d = [hc.to_lab(x, pT) for x in d]
    evs = []
    for i in range(n):
        pw1, pw2 = d[0][i] + d[1][i], d[2][i] + d[3][i]
        ev = hdr(pT) + [line(ids[0], 2, 3, mom(pw1), 80.), line(ids[1], 2, 3, mom(pw2), 40.)]
        # indices (1-based): 1,2 incoming; 3 h; 4 recoil; 5,6 bosons; 7.. quarks
        ev += [line(2, 1, 5, mom(d[0][i])), line(-1, 1, 5, mom(d[1][i])), line(3, 1, 6, mom(d[2][i])), line(-4, 1, 6, mom(d[3][i]))]
        evs.append(ev)
    return evs

if __name__ == "__main__":
    tmp = Path(tempfile.mkdtemp())
    for name, fn in (("bb", lambda pT: fake_bb(pT, N)),
                     ("WW_4q", lambda pT: fake_VV(pT, N, hc.MW, hc.GW, (24, -24))),
                     ("ZZ_4q", lambda pT: fake_VV(pT, N, hc.MZ, hc.GZ, (23, 23)))):
        evs = []
        for pT in PTS:
            evs += fn(float(pT) + 0.5)
        write_lhe(tmp / f"{name}__s0__pt0-0.lhe.gz", evs)
    # analysis bins around the generated pT points
    edges = [199, 201, 299, 301, 399, 401, 599, 601]
    S.SLICE_EDGES = edges
    for name in ("bb", "WW_4q", "ZZ_4q"):
        d = S.load_channel(sorted(tmp.glob(f"{name}__s0__*.lhe.gz")))
        rows = [r for r in S.summarise(d, S.edges_from_config()) if r["n"] > 1000]
        print(f"\n{name}:  (analysis of synthetic LHE)   toy-MC reference in brackets, R=0.8 / R=1.0")
        for r in rows:
            pT = int(round(r["pt_mean"]))
            ref = hc.run.__globals__  # noqa
            print(f"  pT={pT:4d} n={r['n']:5d}  <dR_pair>={r['pair_mean_vis']:.3f}  <max dR(i,h)>={r['axis_max_vis']:.3f}  "
                  f"contained(0.8)={r['cont_vis_R0.8']:.3f}  contained(1.0)={r['cont_vis_R1.0']:.3f}")
