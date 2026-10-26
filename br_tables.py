#!/usr/bin/env python3
import json, numpy as np
import higgs_containment as hc

# ---------------- inputs (edit here) ----------------
BR_H = dict(bb=58.09, WW=21.52, gg=8.180, tautau=6.256, cc=2.884, ZZ=2.641,
            gamgam=0.2270, Zgam=0.1541, ss=0.0246, mumu=0.02171)      # % ; LHCHXSWG YR4, mH=125.09
W = dict(qq=0.6741, e=0.1086, mu=0.1086, tau=0.1086)                  # PDG (lepton universality)
Z = dict(qq=0.6991, nu=0.2000, e=0.03363, mu=0.03366, tau=0.03370)    # PDG
T = dict(h=0.648, e=0.1782, mu=0.1739)                                # tau decays (PDG)
# ----------------------------------------------------
tot = sum(BR_H.values()); print(f"sum of listed H BRs = {tot:.4f}%  (remainder {100-tot:.4f}% = rare/other)")

lW = W['e']+W['mu']; tW = W['tau']
ww = dict(
  q4   = W['qq']**2,
  lvqq = 2*W['qq']*lW,            # l = e,mu
  tvqq = 2*W['qq']*tW,
  lvlv = (lW+tW)**2)
print("WW* sub-BRs:", {k: round(v,5) for k,v in ww.items()}, "sum", round(sum(ww.values()),5))
lZ = Z['e']+Z['mu']
zz = dict(q4=Z['qq']**2, qqll=2*Z['qq']*lZ, qqtt=2*Z['qq']*Z['tau'], qqnn=2*Z['qq']*Z['nu'])
zz['other'] = 1-sum(zz.values())
print("ZZ* sub-BRs:", {k: round(v,5) for k,v in zz.items()})
tt = dict(hh=T['h']**2, hl=2*T['h']*(T['e']+T['mu']), ll=(T['e']+T['mu'])**2)
print("tautau sub-BRs:", {k: round(v,5) for k,v in tt.items()}, "sum", round(sum(tt.values()),5))

# absolute BRs in % of all Higgs decays
A = {}
A['bb'] = BR_H['bb']; A['cc'] = BR_H['cc']; A['gg'] = BR_H['gg']; A['ss'] = BR_H['ss']
A['WW*->qqqq'] = BR_H['WW']*ww['q4']
A['WW*->l nu qq (e,mu)'] = BR_H['WW']*ww['lvqq']
A['WW*->tau nu qq'] = BR_H['WW']*ww['tvqq']
A['WW*->l nu l nu (all l)'] = BR_H['WW']*ww['lvlv']
A['ZZ*->qqqq'] = BR_H['ZZ']*zz['q4']
A['ZZ*->qq l l (e,mu)'] = BR_H['ZZ']*zz['qqll']
A['ZZ*->qq tau tau'] = BR_H['ZZ']*zz['qqtt']
A['ZZ*->qq nu nu'] = BR_H['ZZ']*zz['qqnn']
A['ZZ*->no quarks'] = BR_H['ZZ']*zz['other']
A['tautau->had had'] = BR_H['tautau']*tt['hh']
A['tautau->had lep'] = BR_H['tautau']*tt['hl']
A['tautau->lep lep'] = BR_H['tautau']*tt['ll']
A['Z gamma -> qq gamma'] = BR_H['Zgam']*Z['qq']
A['Z gamma -> other'] = BR_H['Zgam']*(1-Z['qq'])
A['gamma gamma'] = BR_H['gamgam']; A['mu mu'] = BR_H['mumu']
for k,v in A.items(): print(f"{k:28s} {v:8.4f} %")
print("sum", round(sum(A.values()),4))

# ---- Z gamma containment (qq pair) via same machinery
def zgamma(pT, R, n=300000):
    Zp, gam = hc.two_body(hc.MH, n, hc.MZ, 0.0)
    bZ = Zp[:,1:]/Zp[:,[0]]
    a, b = hc.two_body(np.full(n, hc.MZ), n)
    a, b = hc.boost(a, bZ), hc.boost(b, bZ)
    ia = hc.dR_to_axis(hc.to_lab(a, pT)) < R
    ib = hc.dR_to_axis(hc.to_lab(b, pT)) < R
    return np.mean(ia & ib)

# ---- effective (containment-weighted) BRs
res = hc.run()
pts = [(300,0.8),(450,0.8),(600,0.8),(300,1.0),(450,1.0),(600,1.0)]
out = {}
for pT,R in pts:
    r = res[(pT,R)]
    cls = {}
    cls['2-prong hadronic (bb,cc,gg,ss), 2 partons in jet'] = (A['bb']+A['cc']+A['gg']+A['ss'])*r['2body']
    cls['4q (WW*+ZZ*): all 4 in jet'] = (A['WW*->qqqq']*r['WW_4q_all4'] + A['ZZ*->qqqq']*r['ZZ_4q_all4'])
    cls['4q (WW*+ZZ*): exactly 3 in jet'] = (A['WW*->qqqq']*r['WW_4q_3'] + A['ZZ*->qqqq']*r['ZZ_4q_3'])
    cls['4q (WW*+ZZ*): <=2 in jet'] = (A['WW*->qqqq']*(1-r['WW_4q_all4']-r['WW_4q_3']) + A['ZZ*->qqqq']*(1-r['ZZ_4q_all4']-r['ZZ_4q_3']))
    cls['l nu qq (e,mu,tau): qq in jet'] = (A['WW*->l nu qq (e,mu)']+A['WW*->tau nu qq'])*r['WW_lvqq_qq']
    cls['l nu qq (e,mu): qq AND lepton in jet'] = A['WW*->l nu qq (e,mu)']*r['WW_lvqq_qq_and_l']
    cls['ZZ*->qq+(ll,tautau,nunu): qq in jet'] = (A['ZZ*->qq l l (e,mu)']+A['ZZ*->qq tau tau']+A['ZZ*->qq nu nu'])*r['ZZ_qqX_qq']
    cls['tautau (all): both tau in jet'] = (A['tautau->had had']+A['tautau->had lep']+A['tautau->lep lep'])*r['2body']
    cls['Z gamma->qq gamma: qq in jet'] = A['Z gamma -> qq gamma']*zgamma(pT,R)
    out[(pT,R)] = cls
    print(f"\npT={pT} R={R}")
    for k,v in cls.items(): print(f"  {k:52s} {v:7.3f} %")
    inj = cls['2-prong hadronic (bb,cc,gg,ss), 2 partons in jet']+cls['4q (WW*+ZZ*): all 4 in jet']
    print(f"  --> fully-contained hadronic (2-prong + 4q): {inj:6.2f} % of all H;  + 3q: {inj+cls['4q (WW*+ZZ*): exactly 3 in jet']:6.2f} %")
json.dump({f"{k[0]}_{k[1]}": v for k,v in out.items()}, open('effective_BR.json','w'), indent=1)

# sanity check vs CMS HIG-24-008: H4q:H3q  ~ 28:14 for hadronic WW*
print("\nSanity: P(4q)/(P(4q)+P(3q)) for WW*->4q, R=0.8")
for pT in [350,400,450,500,600]:
    r=res[(pT,0.8)]; print(pT, round(r['WW_4q_all4']/(r['WW_4q_all4']+r['WW_4q_3']),3))
