#!/usr/bin/env python3
"""
heft_higgs_pt_study.py
======================
Generate  p p -> h j  (HEFT, 13.6 TeV, LO) with the Higgs decayed at matrix-element level,
sliced in pT(h), and study the angular separation of the Higgs decay products directly
from the LHE files (no shower, no detector).

  python heft_higgs_pt_study.py list
  python heft_higgs_pt_study.py gen     --mg5 /path/to/mg5_aMC [--channels core|all|bb,gg,...] [--dry-run]
  python heft_higgs_pt_study.py analyze [--channels ...]

Physics set-up
--------------
* Pure  p p > h  has pT(h)=0 at LO, so the process is  p p > h j.  At LO pT(h) = pT(j), so the
  run_card cut  ptj >= pT_lo (and ptjmax < pT_hi)  *is* a cut/slice on pT(h).
* cut_decays = F : the run_card cuts act only on the production-level particles, not on the
  h-decay products (otherwise ptj would be applied to the b's, quarks, ...).
* pT slices: the pT(h) spectrum falls steeply, so one inclusive pT>100 GeV run of 10k events has
  only O(100) events above 600 GeV.  Default: 10 slices x 1000 events = 10k events per final state.
  The slices are conditional samples: we only study  <DeltaR>(pT)  and containment(pT), so no
  cross-section weights are needed.  (--inclusive gives one 10k sample with pT(h)>100.)
* V* is generated through the explicit chain  h > w+ w-, w+ > ..., w- > ...  with a large
  bwcutoff so that the off-shell boson is sampled down to ~1 GeV (the physical m_W* distribution
  peaks near 35-40 GeV, and the default bwcutoff=15 would truncate it at m > ~49 GeV).
  The analysis plots the generated m(V*) against the analytic dGamma/dq^2 as a check.
"""
import argparse, gzip, math, os, shutil, subprocess, sys, csv
from pathlib import Path
import numpy as np

# =============================== configuration ===============================
EBEAM = 6800.0                        # GeV per beam -> 13.6 TeV
MH = 125.0                            # HEFT default m_h (param_card); used only for reference curves
PDF = dict(pdlabel="lhapdf", lhaid=331900)   # same as your Type III set-up; use --no-lhapdf to disable
N_PER_CHANNEL = 10000
SLICE_EDGES = [100, 150, 200, 250, 300, 400, 500, 650, 800, 1000, -1]   # pT(h) slices [GeV]; -1 = open
RADII = [0.8, 1.0, 1.2]               # large-R radii for the containment study
TARGETS = [0.5, 0.8, 0.9]             # containment levels whose pT threshold is reported
FIVE_FLAVOUR = False                  # True only if the heft model in your MG5 has a massless b

# Each channel: list of decay strings ('add process' per entry), optional-flag, proxy channel and
# boson type for the V* mass check.  MG5 runs  p p > h j, <decay>.
CHANNELS = {
    # ---- two-body ----
    "bb":      dict(procs=["h > b b~"]),
    "gg":      dict(procs=["h > g g"]),
    "cc":      dict(procs=["h > c c~"], optional=True, proxy="bb"),      # needs a charm Yukawa in the model
    "tautau":  dict(procs=["h > ta+ ta-"], optional=True),
    # ---- WW* ----
    "WW_4q":   dict(procs=["h > w+ w-, w+ > j j, w- > j j"], vv="W"),
    "WW_lvqq": dict(procs=["h > w+ w-, w+ > l+ vl, w- > j j", "h > w+ w-, w+ > j j, w- > l- vl~"], vv="W"),
    "WW_tvqq": dict(procs=["h > w+ w-, w+ > ta+ vt, w- > j j", "h > w+ w-, w+ > j j, w- > ta- vt~"], vv="W"),
    "WW_lvlv": dict(procs=["h > w+ w-, w+ > l+ vl, w- > l- vl~"], vv="W"),
    "WW_tvlv": dict(procs=["h > w+ w-, w+ > ta+ vt, w- > l- vl~", "h > w+ w-, w+ > l+ vl, w- > ta- vt~"], vv="W"),
    "WW_tvtv": dict(procs=["h > w+ w-, w+ > ta+ vt, w- > ta- vt~"], vv="W"),
    # ---- ZZ* ----
    "ZZ_4q":   dict(procs=["h > z z, z > j j, z > j j"], vv="Z"),
    "ZZ_qqll": dict(procs=["h > z z, z > j j, z > l+ l-"], vv="Z"),
    "ZZ_qqtt": dict(procs=["h > z z, z > j j, z > ta+ ta-"], vv="Z"),
    "ZZ_qqvv": dict(procs=["h > z z, z > j j, z > vl vl~"], vv="Z"),
    "ZZ_4l":   dict(procs=["h > z z, z > l+ l-, z > l+ l-"], vv="Z"),
    "ZZ_2l2v": dict(procs=["h > z z, z > l+ l-, z > vl vl~"], vv="Z"),
    # ---- rare (need loop-induced/Yukawa couplings that the stock heft model may not provide) ----
    "Zgam_qq": dict(procs=["h > z a, z > j j"], optional=True),
    "gamgam":  dict(procs=["h > a a"], optional=True),
    "mumu":    dict(procs=["h > mu+ mu-"], optional=True),
}
GROUPS = {
    "core": ["bb", "gg", "cc", "tautau", "WW_4q", "WW_lvqq", "WW_tvqq", "ZZ_4q", "ZZ_qqll", "ZZ_qqvv"],
    "all": list(CHANNELS),
}
# pairs used in plots (labels)
HAD_PIDS = {1, 2, 3, 4, 5, 21}
VIS_PIDS = HAD_PIDS | {11, 13, 15, 22}        # everything except neutrinos


# ================================ MG5 driver ================================
def slices_from_edges(edges):
    return [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]


def mg5_script(name, spec, workdir, slices, nev_per_slice, seed0, nb_core, lhapdf):
    outdir = f"./{name}"
    L = [
        "set automatic_html_opening False --no_save",
        "set notification_center False --no_save",
        "set zerowidth_tchannel False --no_save",
        f"set nb_core {nb_core} --no_save",
        "import model heft",
    ]
    flav = "g u c d s b u~ c~ d~ s~ b~" if FIVE_FLAVOUR else "g u c d s u~ c~ d~ s~"
    L += [f"define p = {flav}", f"define j = {flav}",
          "define l+ = e+ mu+", "define l- = e- mu-"]
    for i, pr in enumerate(spec["procs"]):
        L.append(("generate " if i == 0 else "add process ") + f"p p > h j, {pr}")
    L.append(f"output {outdir} -f")
    vv = spec.get("vv")
    bw = {"W": 38, "Z": 36}.get(vv)          # window m_V - bw*Gamma_V reaches ~1 GeV
    for k, (lo, hi) in enumerate(slices):
        L += [f"launch {outdir} --name=s{k}",
              "shower = OFF", "detector = OFF", "analysis = OFF", "madspin = OFF", "reweight = OFF", "done"]
        S = [f"set ebeam1 {EBEAM:g}", f"set ebeam2 {EBEAM:g}"]
        if lhapdf:
            S += [f"set pdlabel {PDF['pdlabel']}", f"set lhaid {PDF['lhaid']}"]
        S += ["set use_syst False",
              f"set nevents {nev_per_slice}",
              f"set iseed {seed0 + k}",
              "set cut_decays False",                       # do NOT cut the h decay products
              f"set ptj {lo}", f"set ptb {lo}",             # at LO: pT(h) = pT(recoil jet)
              f"set ptjmax {hi}", f"set ptbmax {hi}",
              "set etaj -1", "set etab -1"]                 # no eta cut: DeltaR depends only on pT
        if bw:
            S.append(f"set bwcutoff {bw}")
        L += S + ["done"]
    return "\n".join(L) + "\n"


def cmd_gen(a):
    names = resolve_channels(a.channels)
    slices = [(100, -1)] if a.inclusive else slices_from_edges(SLICE_EDGES)
    nev = int(math.ceil(a.events / len(slices)))
    work = Path(a.workdir).resolve(); work.mkdir(parents=True, exist_ok=True)
    lhe_dir = Path(a.lhe_dir).resolve(); lhe_dir.mkdir(parents=True, exist_ok=True)
    print(f"{len(names)} channels x {len(slices)} slices x {nev} events = {len(names)*len(slices)*nev} events")
    for ic, name in enumerate(names):
        spec = CHANNELS[name]
        script = work / f"{name}.mg5"
        script.write_text(mg5_script(name, spec, work, slices, nev, a.seed + 1000 * ic, a.nb_core,
                                     not a.no_lhapdf))
        print(f"[{name}] wrote {script}")
        if a.dry_run:
            continue
        log = work / f"{name}.log"
        with open(log, "w") as fl:
            rc = subprocess.call([a.mg5, str(script)], cwd=work, stdout=fl, stderr=subprocess.STDOUT)
        got = 0
        for k, (lo, hi) in enumerate(slices):
            src = work / name / "Events" / f"s{k}" / "unweighted_events.lhe.gz"
            if src.exists():
                dst = lhe_dir / f"{name}__s{k}__pt{lo}-{hi}.lhe.gz"
                shutil.copy(src, dst); got += 1
        status = "OK" if got == len(slices) else "INCOMPLETE"
        if got < len(slices) and spec.get("optional"):
            status += " (optional channel: model probably lacks the coupling; see log; proxy: %s)" % spec.get("proxy")
        print(f"[{name}] mg5 rc={rc}, LHE files: {got}/{len(slices)}  -> {status}   (log: {log})")
        if a.clean and got == len(slices):
            shutil.rmtree(work / name, ignore_errors=True)


# ================================ LHE reader ================================
def read_lhe(path):
    op = gzip.open if str(path).endswith(".gz") else open
    with op(path, "rt") as f:
        buf, inside = [], False
        for line in f:
            if line.startswith("<event"):
                inside, buf = True, []
            elif line.startswith("</event"):
                inside = False
                yield parse_event(buf)
            elif inside:
                buf.append(line)


def parse_event(buf):
    nup = int(buf[0].split()[0])
    pid = np.empty(nup, int); st = np.empty(nup, int); m1 = np.empty(nup, int); p = np.empty((nup, 4))
    for i in range(nup):
        t = buf[1 + i].split()
        pid[i], st[i], m1[i] = int(t[0]), int(t[1]), int(t[2])
        p[i] = (float(t[9]), float(t[6]), float(t[7]), float(t[8]))        # E, px, py, pz
    return pid, st, m1, p


def rap_phi(p):
    E, px, py, pz = p[..., 0], p[..., 1], p[..., 2], p[..., 3]
    y = 0.5 * np.log(np.maximum(E + pz, 1e-12) / np.maximum(E - pz, 1e-12))
    return y, np.arctan2(py, px)


def dR(y1, p1, y2, p2):
    dphi = (p1 - p2 + np.pi) % (2 * np.pi) - np.pi
    return np.hypot(y1 - y2, dphi)


def analyse_event(ev):
    pid, st, m1, p = ev
    ih = np.where(pid == 25)[0]
    if ih.size == 0:
        return None
    ih = ih[0]
    # all final-state particles descending from the Higgs (mother chain walk, 1-based mothers)
    desc = []
    for i in np.where(st == 1)[0]:
        j = m1[i]
        while j > 0:
            if j - 1 == ih:
                desc.append(i); break
            j = m1[j - 1]
    desc = np.array(desc, int)
    if desc.size == 0:
        return None
    ph = p[ih]
    yh, phih = rap_phi(ph[None, :]); yh, phih = yh[0], phih[0]
    r = dict(pt=math.hypot(ph[1], ph[2]))
    for tag, S in (("vis", VIS_PIDS), ("had", HAD_PIDS)):
        sel = np.array([i for i in desc if abs(pid[i]) in S], int)
        r["n" + tag] = sel.size
        if sel.size == 0:
            r["axis_" + tag] = np.nan; r["pairmean_" + tag] = np.nan; r["pairmax_" + tag] = np.nan
            continue
        y, ph_ = rap_phi(p[sel])
        r["axis_" + tag] = float(np.max(dR(y, ph_, yh, phih)))
        if sel.size > 1:
            iu = np.triu_indices(sel.size, 1)
            d = dR(y[iu[0]], ph_[iu[0]], y[iu[1]], ph_[iu[1]])
            r["pairmean_" + tag] = float(d.mean()); r["pairmax_" + tag] = float(d.max())
        else:
            r["pairmean_" + tag] = np.nan; r["pairmax_" + tag] = np.nan
    # masses of intermediate V (pdg 23, +-24) whose mother is the Higgs
    mv = []
    for i in np.where((np.abs(pid) == 23) | (np.abs(pid) == 24))[0]:
        if m1[i] - 1 == ih:
            q = p[i]; mv.append(math.sqrt(max(q[0]**2 - q[1]**2 - q[2]**2 - q[3]**2, 0.0)))
    r["mV"] = sorted(mv)
    return r


KEYS = ["pt", "nvis", "nhad", "axis_vis", "axis_had", "pairmean_vis", "pairmax_vis", "pairmean_had", "pairmax_had"]


def load_channel(files):
    cols = {k: [] for k in KEYS}; mlow, mhigh = [], []
    for f in files:
        for ev in read_lhe(f):
            r = analyse_event(ev)
            if r is None:
                continue
            for k in KEYS:
                cols[k].append(r[k])
            if len(r["mV"]) == 2:
                mlow.append(r["mV"][0]); mhigh.append(r["mV"][1])
    out = {k: np.array(v, float) for k, v in cols.items()}
    out["mlow"], out["mhigh"] = np.array(mlow), np.array(mhigh)
    return out


# ================================ summaries ================================
def edges_from_config():
    e = list(SLICE_EDGES); e[-1] = 1e9 if e[-1] < 0 else e[-1]
    return e


def summarise(d, edges):
    rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (d["pt"] >= lo) & (d["pt"] < hi)
        n = int(m.sum())
        if n == 0:
            continue
        row = dict(pt_lo=lo, pt_hi=hi, n=n, pt_mean=float(d["pt"][m].mean()),
                   pair_mean_vis=float(np.nanmean(d["pairmean_vis"][m])) if np.isfinite(d["pairmean_vis"][m]).any() else np.nan,
                   pair_max_vis=float(np.nanmean(d["pairmax_vis"][m])) if np.isfinite(d["pairmax_vis"][m]).any() else np.nan,
                   axis_max_vis=float(np.nanmean(d["axis_vis"][m])) if np.isfinite(d["axis_vis"][m]).any() else np.nan)
        for R in RADII:
            row[f"cont_vis_R{R}"] = float(np.mean(d["axis_vis"][m] < R)) if np.isfinite(d["axis_vis"][m]).any() else np.nan
            row[f"cont_had_R{R}"] = float(np.mean(d["axis_had"][m] < R)) if np.isfinite(d["axis_had"][m]).any() else np.nan
        rows.append(row)
    return rows


def crossing(x, y, target):
    """smallest x at which y first reaches `target` (linear interpolation), NaN if never"""
    x = np.asarray(x); y = np.asarray(y)
    for i in range(len(x)):
        if y[i] >= target:
            if i == 0:
                return float(x[0])
            return float(x[i - 1] + (target - y[i - 1]) * (x[i] - x[i - 1]) / (y[i] - y[i - 1]))
    return float("nan")


_trapz = getattr(np, 'trapezoid', None) or np.trapz


def analytic_vstar(mV, GV, q):
    """normalised dGamma/dm* (m* = q) for H -> V V*  (same formula as the toy MC)"""
    q2 = q**2
    lam = (MH**2 - mV**2 - q2)**2 - 4 * mV**2 * q2
    f = np.sqrt(np.maximum(lam, 0)) * (np.maximum(lam, 0) + 12 * mV**2 * q2) / ((q2 - mV**2)**2 + (mV * GV)**2) * 2 * q
    return f


def cmd_analyze(a):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    names = resolve_channels(a.channels)
    lhe_dir, out = Path(a.lhe_dir), Path(a.out); out.mkdir(parents=True, exist_ok=True)
    edges = edges_from_config()
    data, label = {}, {}
    for n in names:
        files = sorted(lhe_dir.glob(f"{n}__s*.lhe.gz")) + sorted(lhe_dir.glob(f"{n}__s*.lhe"))
        lab = n
        if not files and CHANNELS[n].get("proxy"):
            px = CHANNELS[n]["proxy"]
            files = sorted(lhe_dir.glob(f"{px}__s*.lhe.gz")); lab = f"{n} (proxy {px})"
        if not files:
            print(f"[{n}] no LHE files, skipped"); continue
        data[n] = load_channel(files); label[n] = lab
        print(f"[{n}] {len(data[n]['pt'])} events from {len(files)} files")
    thr_rows, summ = [], {}
    for n, d in data.items():
        rows = summarise(d, edges); summ[n] = rows
        with open(out / f"summary_{n}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
        x = [r["pt_mean"] for r in rows]
        for R in RADII:
            y = [r[f"cont_vis_R{R}"] for r in rows]
            thr_rows.append(dict(channel=label[n], R=R, **{f"pT_at_{int(t*100)}pct": crossing(x, y, t) for t in TARGETS}))
    with open(out / "pt_thresholds.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(thr_rows[0].keys())); w.writeheader(); w.writerows(thr_rows)
    print("\npT(h) [GeV] at which ALL visible decay products (no neutrinos) lie within dR<R of the h axis")
    print(f"{'channel':26s} {'R':>4s} " + " ".join(f"{int(t*100):>5d}%" for t in TARGETS))
    for r in thr_rows:
        print(f"{r['channel']:26s} {r['R']:4.1f} " + " ".join(f"{r[f'pT_at_{int(t*100)}pct']:6.0f}" for t in TARGETS))

    # ---- figures
    had = [n for n in data if n in ("bb", "gg", "cc", "WW_4q", "ZZ_4q", "WW_lvqq", "WW_tvqq", "ZZ_qqll", "ZZ_qqvv", "tautau")]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    for n in had:
        x = [r["pt_mean"] for r in summ[n]]
        ax[0].plot(x, [r["pair_mean_vis"] for r in summ[n]], "o-", ms=3, label=label[n])
        ax[1].plot(x, [r["axis_max_vis"] for r in summ[n]], "o-", ms=3, label=label[n])
    xx = np.linspace(100, 1500, 200)
    ax[0].plot(xx, 2 * MH / xx, "k--", lw=1, label=r"$2m_H/p_T$ (2-body minimum)")
    ax[0].set_ylabel(r"$\langle\Delta R_{ij}\rangle$ (all visible pairs)"); ax[1].set_ylabel(r"$\langle\max_i \Delta R(i,h)\rangle$")
    for A in ax:
        A.set_xlabel(r"$p_T(h)$ [GeV]"); A.set_xscale("log"); A.set_yscale("log"); A.grid(alpha=.3)
    ax[1].axhline(0.8, c="gray", ls=":"); ax[1].axhline(1.0, c="gray", ls="--"); ax[0].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(out / "separation_vs_pt.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(1, 3, figsize=(16, 4.5), sharey=True)
    for iR, R in enumerate(RADII):
        for n in had:
            ax[iR].plot([r["pt_mean"] for r in summ[n]], [r[f"cont_vis_R{R}"] for r in summ[n]], "o-", ms=3, label=label[n])
        ax[iR].set_title(f"anti-$k_t$ R={R}: all visible products inside"); ax[iR].set_xlabel(r"$p_T(h)$ [GeV]")
        ax[iR].set_xscale("log"); ax[iR].grid(alpha=.3)
    ax[0].set_ylabel("contained fraction"); ax[0].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(out / "containment_vs_pt.png", dpi=150); plt.close(fig)

    vv = [n for n in data if CHANNELS[n].get("vv") and data[n]["mlow"].size]
    if vv:
        fig, ax = plt.subplots(1, len(vv), figsize=(4.2 * len(vv), 3.6), squeeze=False)
        for A, n in zip(ax[0], vv):
            mV, GV = (80.377, 2.085) if CHANNELS[n]["vv"] == "W" else (91.1876, 2.4952)
            A.hist(data[n]["mlow"], bins=40, range=(0, MH - mV), density=True, histtype="step", label="MG5 (LHE)")
            q = np.linspace(0.5, MH - mV, 400); f = analytic_vstar(mV, GV, q); A.plot(q, f / _trapz(f, q), "r--", label="analytic")
            A.set_title(n); A.set_xlabel(r"$m_{V^*}$ [GeV]"); A.legend(fontsize=7)
        fig.tight_layout(); fig.savefig(out / "vstar_mass_check.png", dpi=150); plt.close(fig)
    print(f"\nresults in {out}/ : summary_<channel>.csv, pt_thresholds.csv, *.png")


# ================================== misc ==================================
def resolve_channels(arg):
    if arg in GROUPS:
        return GROUPS[arg]
    names = [s.strip() for s in arg.split(",") if s.strip()]
    bad = [n for n in names if n not in CHANNELS]
    if bad:
        sys.exit(f"unknown channel(s) {bad}; use 'list'")
    return names


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    g = sub.add_parser("gen")
    g.add_argument("--mg5", default=os.environ.get("MG5_EXE", "mg5_aMC"))
    g.add_argument("--channels", default="core"); g.add_argument("--events", type=int, default=N_PER_CHANNEL)
    g.add_argument("--workdir", default="work"); g.add_argument("--lhe-dir", default="lhe")
    g.add_argument("--nb-core", type=int, default=16); g.add_argument("--seed", type=int, default=1000)
    g.add_argument("--inclusive", action="store_true", help="single sample with pT(h)>100 instead of slices")
    g.add_argument("--no-lhapdf", action="store_true"); g.add_argument("--dry-run", action="store_true")
    g.add_argument("--clean", action="store_true", help="delete MG5 process dirs once the LHE files are copied")
    an = sub.add_parser("analyze")
    an.add_argument("--channels", default="all"); an.add_argument("--lhe-dir", default="lhe"); an.add_argument("--out", default="results")
    a = ap.parse_args()
    if a.cmd == "list":
        for k, v in CHANNELS.items():
            print(f"{k:9s} {'(optional) ' if v.get('optional') else '           '}{' | '.join(v['procs'])}")
        print("groups:", {k: len(v) for k, v in GROUPS.items()})
    elif a.cmd == "gen":
        cmd_gen(a)
    else:
        cmd_analyze(a)


if __name__ == "__main__":
    main()
