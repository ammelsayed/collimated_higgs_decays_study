#!/usr/bin/env python3
"""
Parton-level toy MC: probability that the decay products of a Higgs boson with given pT
(eta_H = 0) lie inside an anti-kt large-R jet axis cone, dR(parton, H axis) < R.

Decay chains (m_H = 125.09 GeV, isotropic H rest frame, spin correlations neglected):
  2-body : H -> bb, cc, gg, tautau            (massless daughters)
  4-body : H -> V V*  -> f f f f              (V on shell, V* mass from the
           dGamma/dq^2 ~ lam^{1/2}(lam + 12 mV^2 q^2) / ((q^2-mV^2)^2 + mV^2 GV^2) )
Containment is evaluated per daughter, then combined per final-state class.
"""
import numpy as np

rng = np.random.default_rng(12345)
MH, MW, GW, MZ, GZ = 125.09, 80.377, 2.085, 91.1876, 2.4952

def lam(a, b, c):
    return a*a + b*b + c*c - 2*a*b - 2*a*c - 2*b*c

def boost(p, beta):
    """p: (N,4) = (E,px,py,pz); beta: (N,3). Rest frame -> frame where system moves with +beta."""
    b2 = np.sum(beta**2, axis=1)
    g = 1.0/np.sqrt(1.0 - b2)
    bp = np.sum(beta*p[:, 1:], axis=1)
    coef = np.where(b2 > 0, (g - 1.0)*bp/np.where(b2 > 0, b2, 1.0), 0.0) + g*p[:, 0]
    E = g*(p[:, 0] + bp)
    p3 = p[:, 1:] + coef[:, None]*beta
    return np.column_stack([E, p3])

def iso_dirs(n):
    c = rng.uniform(-1, 1, n); ph = rng.uniform(0, 2*np.pi, n)
    s = np.sqrt(1 - c*c)
    return np.column_stack([s*np.cos(ph), s*np.sin(ph), c])

def two_body(M, n, m1=0.0, m2=0.0):
    """Isotropic 2-body decay in rest frame of mass M (array or scalar). returns p1,p2 (n,4)"""
    M = np.broadcast_to(np.asarray(M, float), (n,))
    L = lam(M**2, m1**2, m2**2)
    p = np.sqrt(np.maximum(L, 0))/(2*M)
    d = iso_dirs(n)
    p1 = np.column_stack([np.sqrt(m1**2 + p**2), p[:, None]*d]) if False else \
         np.column_stack([np.sqrt(m1**2 + p**2), p[:, None]*d])
    p2 = np.column_stack([np.sqrt(m2**2 + p**2), -p[:, None]*d])
    return p1, p2

def sample_virtual_mass(mV, GV, n):
    """sample q (mass of V*) in [0, mH-mV] from dGamma/dq^2 above"""
    qmax2 = (MH - mV)**2
    grid = np.linspace(1e-3, qmax2, 4000)
    def f(q2):
        l = lam(MH**2, mV**2, q2)
        return np.sqrt(np.maximum(l, 0))*(l + 12*mV**2*q2)/((q2 - mV**2)**2 + (mV*GV)**2)
    fmax = f(grid).max()*1.02
    out = np.empty(0)
    while out.size < n:
        q2 = rng.uniform(0, qmax2, 4*n)
        keep = rng.uniform(0, fmax, 4*n) < f(q2)
        out = np.concatenate([out, np.sqrt(q2[keep])])
    return out[:n]

def to_lab(p, pT):
    """boost from H rest frame to lab with H at eta=0, phi=0, transverse momentum pT"""
    E = np.sqrt(pT**2 + MH**2)
    beta = np.zeros((p.shape[0], 3)); beta[:, 0] = pT/E
    return boost(p, beta)

def dR_to_axis(p):
    pt = np.hypot(p[:, 1], p[:, 2])
    eta = np.arcsinh(p[:, 3]/np.maximum(pt, 1e-12))
    phi = np.arctan2(p[:, 2], p[:, 1])
    return np.hypot(eta, phi)

def decay_VVstar(mV, GV, n):
    """returns list [d1,d2 (from on-shell V), d3,d4 (from V*)] in H rest frame, plus m*"""
    mstar = sample_virtual_mass(mV, GV, n)
    V, Vs = two_body(MH, n, mV, mstar)                      # V and V* in H frame
    bV  = V[:, 1:]/V[:, [0]]
    bVs = Vs[:, 1:]/Vs[:, [0]]
    a1, a2 = two_body(np.full(n, mV), n)
    b1, b2 = two_body(mstar, n)
    return [boost(a1, bV), boost(a2, bV), boost(b1, bVs), boost(b2, bVs)], mstar

PT_GRID = [200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 1000]
RADII = [0.8, 1.0]
N = 400000

def run():
    res = {}
    for pT in PT_GRID:
        for R in RADII:
            r = {}
            # ---- 2-body (bb, cc, gg, tautau)
            a, b = two_body(MH, N)
            ina = dR_to_axis(to_lab(a, pT)) < R
            inb = dR_to_axis(to_lab(b, pT)) < R
            r['2body'] = np.mean(ina & inb)
            # ---- WW*
            d, ms = decay_VVstar(MW, GW, N)
            inn = [dR_to_axis(to_lab(x, pT)) < R for x in d]
            nin = sum(x.astype(int) for x in inn)
            r['WW_4q_all4'] = np.mean(nin == 4)
            r['WW_4q_3'] = np.mean(nin == 3)
            r['WW_4q_2'] = np.mean(nin == 2)
            r['WW_4q_le1'] = np.mean(nin <= 1)
            # semileptonic: hadronic W is on-shell (d0,d1) or off-shell (d2,d3); lepton is a member of the other pair
            # lepton = one of the two daughters of leptonic V (charged lepton picked at random)
            pick = rng.integers(0, 2, N).astype(bool)
            # case A: hadronic = on-shell V, leptonic = V*
            qqA = inn[0] & inn[1]
            lepA = np.where(pick, inn[2], inn[3])
            # case B: hadronic = V*, leptonic = on-shell V
            qqB = inn[2] & inn[3]
            lepB = np.where(pick, inn[0], inn[1])
            r['WW_lvqq_qq'] = 0.5*(np.mean(qqA) + np.mean(qqB))
            r['WW_lvqq_qq_and_l'] = 0.5*(np.mean(qqA & lepA) + np.mean(qqB & lepB))
            r['WW_lvqq_l_in'] = 0.5*(np.mean(lepA) + np.mean(lepB))
            # fully leptonic: both charged leptons inside
            lA = np.where(pick, inn[2], inn[3]); lB = np.where(rng.integers(0, 2, N).astype(bool), inn[0], inn[1])
            r['WW_lvlv_both_l'] = np.mean(lA & lB)
            # ---- ZZ*
            d, ms = decay_VVstar(MZ, GZ, N)
            inn = [dR_to_axis(to_lab(x, pT)) < R for x in d]
            nin = sum(x.astype(int) for x in inn)
            r['ZZ_4q_all4'] = np.mean(nin == 4)
            r['ZZ_4q_3'] = np.mean(nin == 3)
            r['ZZ_4q_2'] = np.mean(nin == 2)
            # ZZ*->qq + (ll or vv): hadronic pair is on-shell or off-shell with equal weight
            qqA = inn[0] & inn[1]; qqB = inn[2] & inn[3]
            r['ZZ_qqX_qq'] = 0.5*(np.mean(qqA) + np.mean(qqB))
            r['ZZ_qqll_qq_and_ll'] = 0.5*(np.mean(qqA & inn[2] & inn[3]) + np.mean(qqB & inn[0] & inn[1]))
            res[(pT, R)] = r
    return res

if __name__ == "__main__":
    res = run()
    import json
    out = {f"{pT}_{R}": v for (pT, R), v in res.items()}
    json.dump(out, open('/home/claude/containment.json', 'w'), indent=1)
    keys = ['2body','WW_4q_all4','WW_4q_3','WW_4q_2','WW_lvqq_qq','WW_lvqq_qq_and_l','WW_lvqq_l_in',
            'ZZ_4q_all4','ZZ_qqX_qq','ZZ_qqll_qq_and_ll']
    for R in RADII:
        print(f"\nR = {R}")
        print("pT    " + "  ".join(f"{k[:16]:>16s}" for k in keys))
        for pT in PT_GRID:
            r = res[(pT, R)]
            print(f"{pT:5d} " + "  ".join(f"{r[k]:16.3f}" for k in keys))
