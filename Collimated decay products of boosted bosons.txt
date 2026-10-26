# Collimated decay products of boosted bosons

> Exported 10/26/2026, 8:23:29 AM  
> Source: https://claude.ai/chat/4e3b049f-3249-4d53-91a4-3d5a3ccde3aa


*2026-10-25T23:29:42.269205Z*

So i know that when the W and Z bosons are boosted enough, their hadronic products become very collimated such that the bosons are better reconstructed a one large-R jet instead of two resolved small-R jets. However, for the H boson for example, 55% of its decay modes are bb~, WW, ZZ, tautau, gg, gamama, etc. Are these also going to be very collimianted, and when the W and Z also decay hadronically will the Higgs boson get reconstructed as a large-R jet? What when one of the W or Z decay leptonically and the other handrnically? Then we are going to have a 2-prong jet with leptons and neutrinos inside?

---


*2026-10-25T23:30:14.299694Z*

## Short answer

Yes, all of these are collimated, but collimation and large-R jet reconstruction are two separate questions.

- **Collimation** is pure two-body kinematics and is independent of the decay channel.
- **Large-R jet reconstruction** depends on whether the decay products are hadronic, so that the calorimeter sees them as a jet.

## Kinematics

For a two-body decay of a particle of mass m and transverse momentum pT, with momentum fractions z and 1−z:

$$\Delta R \simeq \frac{m}{p_T\sqrt{z(1-z)}} \;\geq\; \frac{2m}{p_T}$$

For the Higgs, m_H = 125 GeV gives ΔR ≈ 1 at pT ≈ 250 GeV, so it fits inside an R = 1.0 anti-kt jet (an R = 0.8 jet needs pT ≳ 310 GeV). This holds for every channel. The channel only changes what lives inside the cone.

A small correction to the numbers: bb̄ alone is ≈58%, WW* ≈21%, gg ≈8%, ττ ≈6%, cc̄ ≈3%, ZZ* ≈2.6%, γγ ≈0.23%. Together they are essentially 100% of the Higgs decays.

## Channel by channel

**H → bb̄ (≈58%).** This gives a two-prong large-R jet, the canonical boosted-Higgs signature. It is identified through soft-drop mass, substructure (N₂, D₂), and b-tagging on the subjets or an ML tagger (ParticleNet, ParT, GN2X). Semileptonic b decays put neutrinos inside the jet, which shifts the jet mass low. This is why mass regression is often used.

**H → gg (≈8%), H → cc̄ (≈3%).** The jet is also two-prong, but without b-tag handles it is nearly indistinguishable from QCD, so the sensitivity is poor.

**H → WW\* (≈21%).** Since m_H < 2m_W, one W is on-shell and the other is off-shell, with m_W* ≲ 45 GeV. Both W decays fall inside the same cone, but the sub-cases differ:

- **Fully hadronic (WW* → 4q, ≈45% of WW\*):** a four-prong large-R jet. This is a genuinely different object from a W/Z jet. It is tagged with τ₄/τ₂-type observables or dedicated ML taggers (e.g. "H→4q" classes), and its soft-drop mass is not the usual two-prong peak. The off-shell W* often gives soft or merged prongs.
- **Semileptonic (WW\* → ℓνqq, ≈29% for ℓ = e, μ; ≈44% if τ is included):** this is the case you ask about, and your picture needs one refinement. The jet itself contains only the hadrons, a two-prong qq̄ system from one W. The lepton is nearby, with ΔR(ℓ, J) small, but it is usually reconstructed separately and removed from the jet. The neutrino shows up as MET, approximately collinear with the lepton.
- **Fully leptonic (ℓνℓν):** no jet, just two close-by leptons plus MET.

Three practical consequences for the semileptonic case:

1. Standard isolation fails because the lepton sits inside or adjacent to the jet. You need mini-isolation, ΔR/pT-relative isolation, or a lepton-in-jet ID.
2. The mass is not fully reconstructable. Typical approaches use m(J + ℓ + MET), with MET projected along the lepton (the collinear approximation), or a regression.
3. The jet mass alone is not the Higgs mass, so you must use the combined system or a discriminant.

**H → ττ (≈6%).** The two taus are collimated with ΔR ≈ 2m_H/pT, so standard τ_h reconstruction (HPS with cone ≈ 0.4–0.5) breaks down due to overlap. Dedicated boosted-ττ taggers are needed, with MET and collinear mass or SVfit-like techniques for the mass. τ_h τ_h can show up inside a large-R jet, while leptonic taus are again lepton plus MET.

**H → ZZ\* (≈2.6%).** The same logic as WW\*, with a hadronic Z\* adding more prongs. The 4ℓ final state is clean but collimated leptons need modified isolation.

**H → γγ (≈0.23%).** The photons are not jets. The diphoton mass is reconstructed from two collimated ECAL showers. This is a resolved resonance search, not a large-R jet analysis, although merged photons at very high pT need care.

## Summary table

| Channel | Final state | Large-R jet? | Prongs |
|---|---|---|---|
| bb̄, cc̄, gg | hadronic | yes | 2 |
| WW*→4q, ZZ*→4q | hadronic | yes | 4 |
| WW*→ℓνqq | hadronic + lepton + MET | jet (2-prong) + nearby lepton | 2 + ℓ |
| ττ | τ_h or ℓ + MET | partly (τ_h τ_h merged) | 2 |
| γγ, 4ℓ, ℓνℓν | non-hadronic | no | none |

If you want, I can go through the specific variables used for boosted H→WW* → 4q or ℓνqq (e.g. soft-drop and N-subjettiness definitions, and the collinear-mass construction).

---


*2026-10-25T23:37:57.350870Z*

I care about the large-R jet reconstruction with anti-kt algorithm. Can you help me find from published ATLAS or CMS articles how likely a higgs boson with pT above a certain limit will be more likely to get identified as a large-R jet? I'm susposious that when the Higgs boson decays via WW or ZZ it can still get reconstructed as a large-R jet because altoough the W and Z are colliminated, but their decay products may not, and since the 4q maynot be colliminated enougn to be all reconstructed within one large-R jet. After that, i need you to help me calculate, considering all higgs decays channels in detail, and given that the Higgs boson is suffessiotnly boosted, what is the Branching ratio of all possible higgs decays that could lead the Higgs boson to get reconsticted as a large-R jet? And what is the branching ratio of other channels including those that include leptons and large/small R jets

---


*2026-10-25T23:43:38.405527Z*

I'll start with the published ATLAS and CMS results on containment and tagging of boosted H→WW*→4q and related decays.

Quick status: the containment toy-MC has run. I'm now combining it with the SM branching fractions into the channel-by-channel BR tables, and sanity-checking against the CMS H4q/H3q fractions.

Your suspicion is right: the published numbers and a toy calculation both show that WW*→4q and ZZ*→4q often fail to fit all four quarks in one large-R jet. I found no published ATLAS or CMS table of "fraction of H→WW*→4q fully contained versus pT", so the pT dependence below comes from my own parton-level calculation.

## 1. What the published analyses say

- **CMS H→WW search (CMS-HIG-24-008, JHEP 07 (2026) 248)** states that W bosons from a Higgs with pT ≳ 250 GeV are separated by ΔR < 0.8. That is a statement about the W–W separation, not about quark containment, and the paper's own jet classes show the difference.
  - Jets are classified by how many quarks fall inside the AK8 cone. "3q" explicitly means a quark escaped.
  - In signal events the H candidate is H4q ≈ 28%, H3q ≈ 14% and Hℓqq ≈ 13%, about 55% in total.
  - The other ≈45% are partially boosted topologies, because the candidate-jet pT threshold is only 200 GeV.
  - The companion paper (arXiv:2604.09809) separates 4q and 3q jets for the same reason. Its H→WW* ROC curves use only jets with all four quarks within ΔR < 0.8.
  - It also notes that soft drop (z = 0.1, β = 0) often strips so much that m_SD ≈ 0 for H and t jets.
- **ATLAS H→bb tagging (arXiv:1906.11005)** says that with R = 1.0 the Higgs decay products fall in a single jet "in most cases" if pT^H ≥ 250 GeV, and that the acceptance depends strongly on pT. I did not extract numeric acceptances from its Figure 1.
- **One correction to my earlier answer:** I said the lepton is usually removed from the jet. In CMS, leptons inside the cone are PF candidates and are clustered into the AK8 jet. This is why they use mini-isolation and a "lepton-in-jet" topology.

## 2. Containment toy calculation

**Method.** Parton-level Monte Carlo at m_H = 125.09 GeV with η_H = 0. This loses no generality, since ΔR is invariant under longitudinal boosts at fixed pT.

- Two-body decays (bb, cc, gg, ττ) are isotropic in the H rest frame.
- H→VV* has V on shell and the V* mass drawn from dΓ/dq² ∝ λ^½(λ + 12 m_V² q²) / ((q² − m_V²)² + m_V²Γ_V²), with λ = λ(m_H², m_V², q²). Decays are then isotropic in each V frame, with spin correlations neglected.
- "Contained" means ΔR(parton, H axis) < R, which is the same criterion CMS uses for matching. There is no FSR, hadronization, pileup or parton pT cut.
- Statistics are 4×10⁵ events per point, so the statistical error is below 0.1%.

| pT^H [GeV] | R | bb/cc/gg (2 partons in) | WW*→4q all 4 | WW*→4q exactly 3 | hadronic W (qq) in, from ℓνqq | qq and lepton in |
|---|---|---|---|---|---|---|
| 250 | 0.8 | 0.49 | 0.21 | 0.55 | 0.50 | 0.35 |
| 300 | 0.8 | 0.60 | 0.35 | 0.51 | 0.61 | 0.48 |
| 400 | 0.8 | 0.75 | 0.55 | 0.39 | 0.75 | 0.65 |
| 500 | 0.8 | 0.83 | 0.68 | 0.29 | 0.83 | 0.75 |
| 600 | 0.8 | 0.88 | 0.76 | 0.22 | 0.88 | 0.82 |
| 1000 | 0.8 | 0.95 | 0.91 | 0.09 | 0.95 | 0.93 |
| 250 | 1.0 | 0.64 | 0.40 | 0.49 | 0.65 | 0.52 |
| 400 | 1.0 | 0.83 | 0.69 | 0.29 | 0.83 | 0.76 |
| 600 | 1.0 | 0.92 | 0.84 | 0.15 | 0.92 | 0.88 |
| 1000 | 1.0 | 0.97 | 0.94 | 0.06 | 0.97 | 0.96 |

- **Why 4q is worse.** The two quarks from a single W are contained as well as bb (compare the 2-partons column with the hadronic-W column). The cost comes from needing four partons at once. In the H frame the W and W* carry only about 19 GeV of momentum for m* ≈ 38 GeV, so the four quarks are emitted nearly isotropically, and the worst of the four sets the containment.
- **Where 4q becomes safe.** At R = 0.8, all-four containment reaches ~55% at 400 GeV and ~90% only near 1 TeV. At R = 1.0 it reaches ~90% near 800 GeV.
- **Cross-check against CMS.** For WW*→4q at R = 0.8, my 4q/(4q+3q) fraction is 0.65 at 450 GeV and 0.70 at 500 GeV. CMS's H4q:H3q of 28:14 gives 0.67. The CMS sample mixes pT, so this is only a consistency check.
- **ZZ*→4q** behaves almost identically to WW*→4q.

## 3. Branching ratios (% of all Higgs decays)

Inputs: LHCHXSWG Higgs BRs at m_H = 125.09 GeV, entered from memory, so please verify the last digit. My search only returned snippets agreeing at the 0.3-point level, not the table itself. The W, Z and τ BRs are PDG values: W→qq 67.41%, ℓν 10.86% each; Z→qq 69.91%, νν 20.00%, ℓℓ 3.366% each; τ→hadrons 64.8%. All are editable at the top of `br_tables.py`. The classes sum to 99.995%.

| Class | Channels | BR [%] |
|---|---|---|
| 2-prong hadronic | bb 58.09, gg 8.18, cc 2.88, ss 0.02 | **69.18** |
| 4-quark | WW*→qqqq 9.78, ZZ*→qqqq 1.29 | **11.07** |
| Jet(s) + lepton(s)/MET | WW*→ℓνqq (e,μ) 6.30, WW*→τνqq 3.15, ZZ*→qqℓℓ (e,μ) 0.25, ZZ*→qqττ 0.12, ZZ*→qqνν 0.74 | **10.56** |
| ττ | τhτh 2.63, τhτℓ 2.85, τℓτℓ 0.78 | **6.26** |
| No hadronic prongs | WW*→ℓνℓν 2.28, ZZ*→no quarks 0.24, γγ 0.23, Zγ→non-qq 0.05, μμ 0.02 | **2.82** |
| Z(→qq)γ | jet plus photon | **0.11** |

**Pure-hadronic upper bound.** As pT→∞ the decays that can end up fully inside a large-R jet are the 2-prong and 4-quark classes, **80.25%**. Adding the jet-plus-lepton class gives 90.8% with at least two quark or gluon prongs.

**Containment-weighted BR** (the BR times the containment from Section 2, as % of all H):

| Class | Asymptotic | R=0.8, 300 | R=0.8, 450 | R=0.8, 600 | R=1.0, 450 |
|---|---|---|---|---|---|
| 2-prong, both partons in | 69.18 | 41.6 | 54.8 | 60.6 | 59.6 |
| 4q, all 4 in | 11.07 | 3.85 | 6.88 | 8.46 | 8.21 |
| 4q, exactly 3 in ("3q") | | 5.66 | 3.77 | 2.46 | 2.69 |
| ℓνqq (e,μ,τ), qq in | 9.45 | 5.78 | 7.51 | 8.28 | 8.16 |
| ℓνqq (e,μ), qq and ℓ in | 6.30 | 2.99 | 4.46 | 5.17 | 5.06 |
| ZZ*→qq+X, qq in | 1.11 | 0.68 | 0.88 | 0.97 | 0.96 |
| ττ, both τ in | 6.26 | 3.76 | 4.96 | 5.48 | 5.40 |
| **Fully contained hadronic (2-prong + 4q)** | 80.25 | **45.5** | **61.7** | **69.0** | **67.9** |

For example, at 450 GeV and R = 0.8 about 62% of all Higgs decays end up as a fully contained hadronic jet. Another ≈4% are 3q jets that look like partially reconstructed W-pair decays.

## Caveats

- **Parton-level only.** Detector-level numbers will be lower because of FSR, soft-quark loss, pileup, lepton isolation and ID, and the jet pT threshold.
- **Inclusive in the pT^H spectrum, the classes are not exclusive.** A single jet can enter several rows.
- **Decay-mode dependence.** I applied one set of W/Z/τ BRs to all channels, which ignores small mass effects for the W* at m* ≲ 45 GeV.

If useful, I can add a PyROOT/uproot version that reads your Delphes truth record and computes the same containment per event.

Files are in `higgs_containment.py` (the Monte Carlo) and `br_tables.py` (the BR tables).

---


*2026-10-26T00:02:34.519055Z*

[Attachment: signal.txt]

This is very good work that you have done so far. Now i have a better idea to verify our results with MC simulation tools: madgraph5. I want you to do the following. Write a python script, to use heft, to generate higgs bosons from pp> h collisions at 13.6 TeV. We want to decay the higgs boson at ME element level to all the possible final states. And we want to make its pT insitall high (maybe consider pT(h) > 100 GeV) to that we focus the event generation on the high pT region. Here is what i want to do exactly, for the h>bb/gg/cc we can check the seperation between the final states particles varied with the Higgs boson pT. For the h>ww/zz>4q, we can check the mean seperation between all four final state quarks to understand at which limit they are reconsted as large-R jet fully (we do not need to bother ourselfs with the 3q large-R jets in this simulation). We can also study the other channels as well, the goal is just to know when they can be considered as large-R jets (meaning at which higgs pT). In here i gave you an example of how i write mg5 scripts. We need to generate 10k events for each possible final state, then we study the seperation of the particles difrectly from the LHE file, so no need for any shower or detector similation, these can be set to off

---


*2026-10-26T00:08:09.789264Z*

I'll build the generation driver and the LHE analysis in one script. MG5 isn't installed in this sandbox, so I'll validate the analysis half end-to-end on synthetic LHE files built from the toy MC.

I wrote the generation driver and the LHE analysis as one script, but I could not run it against a real MG5 here, so the MG5 command syntax is untested on your installation. What I did run is the analysis half: I fed it synthetic LHE files built from the earlier toy MC, and it reproduced those containment numbers (for example WW*→4q at 400 GeV, R=0.8: 0.555 against 0.550).

## How to run it

```
python heft_higgs_pt_study.py list                               # channels and their MG5 decay strings
python heft_higgs_pt_study.py gen --mg5 /path/to/mg5_aMC --channels core --nb-core 16
python heft_higgs_pt_study.py analyze --channels all             # CSVs, thresholds table, PNGs
```

`--dry-run` only writes the `.mg5` files so you can inspect them, and `--channels` takes `core`, `all` or a comma list. The script writes one `.mg5` file per channel, in the style of your example (the `set ... --no_save` header, `launch --name=`, shower/detector/MadSpin all OFF). It compiles each channel once and runs all pT slices as successive launches.

## Design decisions

- **`p p > h j`, not `p p > h`.** At LO the Higgs has pT = 0, so a pT(h) > 100 GeV cut would leave no events. The recoil jet balances it, so `ptj`/`ptjmax` act as a slice in pT(h).
- **`cut_decays = False`.** Otherwise `ptj` would also cut the b, quark and gluon decay products of the Higgs.
- **pT slices.** Ten slices of 1000 events each give 10k events per final state. A single inclusive run above 100 GeV would leave only O(100) events above 600 GeV. `--inclusive` gives one 10k sample instead. No cross-section weights are needed, because we only look at ΔR as a function of pT.
- **Off-shell boson sampling.** I use the explicit chain `h > w+ w-, w+ > j j, ...` with `bwcutoff` 38 for W and 36 for Z. The default of 15 would cut the off-shell boson at m ≳ 49 GeV, but the physical W* mass peaks around 35–40 GeV. The analysis plots the generated m(V*) against the analytic curve (`vstar_mass_check.png`) to confirm this.
- **Four-flavour `p` and `j`** by default, to avoid a massive b in the initial state. Set `FIVE_FLAVOUR = True` if your `heft` has a massless b.

## What the analysis does

For each event it takes the Higgs and all final-state particles descending from it via the LHE mother chain. It then computes, per pT(h) bin:

- the mean and maximum pairwise ΔR (the mean over all pairs, 6 for 4q, and the maximum);
- the maximum ΔR(parton, h axis);
- the contained fraction for R = 0.8, 1.0, 1.2, with neutrinos excluded.

It also reports the pT(h) at which containment reaches 50%, 80% and 90%, in `pt_thresholds.csv`.

For comparison, the toy-MC sample gave these pT thresholds for R=0.8 (log-uniform sample, so only rough):

| Channel | 50% | 80% | 90% |
|---|---|---|---|
| bb | ~260 GeV | ~430 GeV | ~650 GeV |
| WW*→4q | ~390 GeV | ~680 GeV | ~850 GeV |
| ZZ*→4q | ~370 GeV | ~650 GeV | ~1 TeV |

If your MG5 curves disagree substantially, check the `bwcutoff` and W* mass plot first.

## Things to check on your MG5

1. **Run card parameter names.** `cut_decays`, `ptjmax`, `ptbmax` and `bwcutoff` are the ones I'm least sure exist under those names in your version. Check with `grep` in the run_card.
2. **Which couplings the stock `heft` model has.** Charm, tau, muon, γγ and Zγ decays may produce "no diagrams". I marked those channels optional, and the script logs the failure and carries on. For `cc` the analysis falls back to the `bb` sample, since the kinematics are identical (quark masses are negligible against m_h/2 ≈ 62 GeV).
3. **Tau decays.** `h > ta+ ta-` leaves the taus undecayed in the LHE, so the tau direction acts as the visible-product direction.
4. **Higgs mass.** It is the `heft` default of 125 GeV (my earlier toy MC used 125.09).

Files are in `heft_higgs_pt_study.py` (generation and analysis) and `selftest_lhe_pipeline.py` (the synthetic-LHE check, which needs `higgs_containment.py` from before).

---


*2026-10-26T00:11:16.895722Z*

you forgot to give me the scripts

---


*2026-10-26T00:11:21.172783Z*

Sorry, I copied the files to the outputs folder but never presented them. Here they are.

`heft_higgs_pt_study.py` is the main script: the MG5 generation driver plus the LHE analysis, with the `list`, `gen` and `analyze` subcommands. `selftest_lhe_pipeline.py` is the synthetic-LHE check. It imports `higgs_containment.py` from the earlier turn, so keep that file in the same folder.

Start with `gen --dry-run` to inspect the generated `.mg5` files before launching MG5.


---
Exported with Claude Export Free
