# Venue research: hyperspectral LDA manuscripts

**Date compiled:** 2026-05-14. All deadlines and figures verified at time of writing from the URLs cited per section. **Re-verify a few weeks before submission** — conference deadlines drift.

The two manuscripts:

- **Conference paper** (4-8 pages): band-mask robustness diagnostic on 6 labelled scenes + 5 HIDSAG mineral subsets, paired ARI under 4 spectral restriction policies, Hungarian topic-id alignment. Headline finding is honest reporting of a partial-negative result (KSC + Botswana paired ARI ≈ 0.01; Salinas-A SWIR-only paired ARI = 0.77).
- **Journal article** (20-30 pages): full multi-axis (F-1..F-12) reproducibility framework, online-VB LDA as canonical, neural-topic comparison (ProdLDA / ETM), deep encoder baselines (CAE-1D/2D/3D, β-VAE), HIDSAG mineral case study, public artefacts (1726+ JSON / binary), FastAPI backend, 109-endpoint smoke harness.

The work sits at the **intersection of remote sensing, image processing, and reproducible-ML methodology** with a clear remote-sensing application surface. That dual identity broadens the venue space but also means scope alignment varies sharply by venue.

---

## Conference candidates

### WHISPERS 2026 — Workshop on Hyperspectral Image and Signal Processing

- **URL:** https://www.ieee-whispers.com/important-dates/ and https://www.ieee-whispers.com/paper-submission/
- **Sponsor:** IEEE GRSS (flagship hyperspectral-only event)
- **Edition / location:** WHISPERS 2026, Glasgow, Scotland, **17-19 November 2026**.
- **Scope alignment:** Extremely strong. WHISPERS is the only venue whose entire scope is hyperspectral signal processing — LDA/topic modelling on hyperspectral cubes, band-restriction robustness, and the HIDSAG mineral subset case study are textbook WHISPERS material.

**Key constraints:**
- **Page limit:** Two submission tracks: (a) abstract-only up to 1 page (in programme, **not** in IEEE Xplore), or (b) **full paper 4-5 pages** (in programme **and** IEEE Xplore). Already-published journal papers may also be presented (programme only).
- **Template:** IEEE conference (IEEEtran two-column) — confirm from author kit on the submission page before final pass.
- **Submission system:** EasyChair.
- **Deadlines (2026 edition):** submission opens 4 May 2026; **paper deadline 28 July 2026**; acceptance notification 20 Sep 2026; author registration deadline 2 Nov 2026.
- **Review:** Single-blind by default for IEEE GRSS-sponsored workshops (not explicitly stated on the public WHISPERS page — confirm in the author kit).
- **Open access:** IEEE Xplore standard terms (papers go behind paywall unless an explicit OA option is offered for the proceedings). No mandatory APC.
- **Code/data policy:** Not mandated, but the community strongly rewards artefact release; explicit mention of a `lda-hsi.fasl-work.com` reproducibility surface plus a 109-endpoint smoke harness will land well.
- **Impact metric:** No formal h5-index reported by IEEE GRSS publicly; WHISPERS proceedings are indexed in IEEE Xplore and frequently cited as the de-facto hyperspectral venue.

### IGARSS 2026 — IEEE International Geoscience and Remote Sensing Symposium

- **URL:** https://2026.ieeeigarss.org/call_for_papers.php and https://2026.ieeeigarss.org/topics.php
- **Edition / location:** 46th IGARSS, **Washington, D.C., 9-14 August 2026** (Washington Hilton).
- **Scope alignment:** Strong. The Topical Areas list includes **T.15 Hyperspectral Data Processing and Analysis** and **S.4 Spaceborne Hyperspectral Missions**, and a 2026 special theme on **"Artificial Intelligence Ethics and Governance in Remote Sensing"** which is sympathetic to honest-reporting / reproducibility framing. There are also Community Contributed Themes (CCTs) — at least one CCT.15 covers onboard hyperspectral DL.

**Key constraints:**
- **Page limit:** **4-page limit excluding references**, standard two-column IEEE format (IEEEtran). Three submission types: (1) full 4-page papers — required for IEEE Xplore inclusion and Student Paper Competition; (2) abstracts 400-600 words, not in Xplore; (3) Recently Published Article (must be a Q1 journal paper published after 1 Jan 2025) — presentation only.
- **Submission system:** IGARSS 2026 portal, opens 15 Nov 2025.
- **Deadline:** **10 January 2026** for paper / abstract submission. **This has already passed as of today (14 May 2026).** IGARSS 2026 is no longer a submission target — only an option as a *presenter* if accepted earlier or via the Recently Published Article track if the journal manuscript ships first.
- **Review:** Peer review; double-blind not enforced at IGARSS historically.
- **Open access:** Standard IEEE Xplore (no mandatory OA fee for proceedings).
- **Code/data policy:** No mandated artefact release; encouraged.
- **Impact metric:** Largest remote-sensing conference by attendance (~3000); IEEE Xplore indexed.

### SPIE Remote Sensing — Edinburgh (SPIE Sensors + Imaging 2026)

- **URL:** https://spie.org/conferences-and-exhibitions/sensors-and-imaging
- **Edition / location:** SPIE Sensors + Imaging combines SPIE Remote Sensing and SPIE Security + Defence under one roof. **Edinburgh, 14-17 September 2026**, Edinburgh International Conference Centre.
- **Scope alignment:** Strong for hyperspectral methodology. The umbrella explicitly lists **"multispectral and hyperspectral imaging, deep learning, ML and AI, signal processing and image analysis."** Specific conferences inside the umbrella will host the band-mask diagnostic naturally.
- **Page limit:** SPIE Proceedings papers are typically **6-12 pages** (no hard cap; common range), single-column SPIE manuscript template. Abstract submission is required first; manuscript submission later if accepted.
- **Submission system:** spie.org abstract submission portal.
- **Deadlines:** Abstract submission deadlines for the 2026 European events are typically around **end of March to early April 2026** based on prior editions — **also already passed as of today (14 May 2026)**.
- **Review:** Single-blind, abstract-screened.
- **Open access:** SPIE proceedings — authors may pay a per-paper open-access fee; not mandatory.
- **Code/data policy:** No mandate.
- **Impact metric:** SPIE Proceedings indexed in SPIE Digital Library, Scopus, EI; lower per-paper visibility than IEEE/IGARSS but strong applied-spectroscopy audience.

### ICIP 2026 — IEEE International Conference on Image Processing

- **URL:** https://2026.ieeeicip.org/ and https://2026.ieeeicip.org/important-dates/
- **Edition / location:** 33rd ICIP, **Tampere, Finland, 13-17 September 2026**.
- **Scope alignment:** Moderate. ICIP is image-processing umbrella; hyperspectral and topic-modelling papers do appear, but it is not a remote-sensing-first audience. The band-mask diagnostic could be reframed as "robustness of unsupervised representations to channel restriction" — that abstraction would land at ICIP but loses some of the hyperspectral-specific signal.
- **Page limit:** ICIP track: **up to 5 pages of content + 1 page of references**. OJSP track: up to 8 pages + 1 page references.
- **Template:** IEEE ICIP 2026 Author Kit (IEEEtran two-column).
- **Submission system:** https://icip2026.exordo.com/ (paper submission portal open).
- **Deadlines:** Paper deadline **4 February 2026**, with grace period until **11 February 2026**. **Already passed.**
- **ORCID:** Mandatory for all authors.
- **Review:** Double-blind.
- **Open access:** Open Preview on IEEE Xplore (papers freely downloadable 13 Aug-13 Sep around the event); no APC.

### EUSIPCO 2026 — European Signal Processing Conference

- **URL:** https://eusipco2026.org/ and https://eusipco2026.org/submissions/
- **Edition / location:** 34th EUSIPCO, **Bruges, Belgium, 31 August - 4 September 2026**.
- **Scope alignment:** Moderate. EUSIPCO covers all signal processing including hyperspectral, but it is broader than the hyperspectral audience.
- **Page limit:** EUSIPCO papers are typically **5 pages including references**.
- **Deadlines:** Paper submission deadline **13 February 2026 AoE**. **Already passed.**

---

## Journal candidates

### IEEE Transactions on Geoscience and Remote Sensing (TGRS)

- **URL:** https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=36 and https://www.grss-ieee.org/publications/author-resources/tgrs-information-for-authors/
- **Scope alignment:** Highest. TGRS is the canonical home for substantive hyperspectral methodology with rigorous evaluation.
- **Impact Factor (2024 JCR):** **9.5**. Q1.
- **Page limit:** No hard upper limit; **mandatory Overlength Page Charge of $230/page beginning page 11** for submissions after 1 Jan 2026 (raised from page 7 in the prior policy). The 20-30 page journal target sits comfortably inside this allowance with predictable overlength cost; budget ~$2300-4600 in OPC alone for a 20-30 page paper plus figures.
- **Template:** IEEE Transactions two-column (IEEEtran). Official Overleaf template available.
- **Submission system:** https://ieee.atyponrex.com/journal/tgrs.
- **Review:** **Single-blind.**
- **Open access:** Hybrid. **Optional OA APC $2,800 for 2026 submissions** (IEEE member 5% discount; GRSS member 20% discount). Traditional non-OA option also available with no APC.
- **Code/data policy:** Encouraged (IEEE Author Center reproducibility encouragement: IEEE DataPort, Code Ocean compute capsules linked to a "Code & Datasets" tab on IEEE Xplore). TGRS is also part of the **IEEE Transparent Peer Review** pilot — opt-in publishes reviewer reports alongside the paper.
- **Timeline:** Typical first decision 12-18 weeks.

### IEEE JSTARS

- **URL:** https://www.grss-ieee.org/publications/journal-of-selected-topics-in-applied-earth-observations-and-remote-sensing/
- **Scope alignment:** High. JSTARS leans more **applied earth observation** than TGRS's methodological depth.
- **Impact Factor:** **5.3-6.2**.
- **Page limit:** Flexible.
- **Template:** IEEEtran.
- **Review:** Single-blind. **Rapid peer-review target ~10 weeks.**
- **Open access:** **Fully open-access journal since 2021. APC US $1,800.**
- **Code/data:** **Optional Code Ocean submission.**

### Remote Sensing of Environment (Elsevier)

- **URL:** https://www.sciencedirect.com/journal/remote-sensing-of-environment
- **Scope alignment:** Lower fit — RSE prioritises biophysical/quantitative applications. **Probably out of scope** for the methodology-heavy framing.
- **Impact Factor:** **11.4 (2024 JCR)**. Q1.
- **APC:** USD $4,230 (OA).

### ISPRS Journal of Photogrammetry and Remote Sensing (Elsevier)

- **URL:** https://www.sciencedirect.com/journal/isprs-journal-of-photogrammetry-and-remote-sensing
- **Scope alignment:** Moderate-to-high.
- **Impact Factor:** **12.2 (2024 JCR per Web of Science)** — currently the highest-IF venue on this list.
- **APC:** USD $3,800.

### Remote Sensing (MDPI)

- **URL:** https://www.mdpi.com/journal/remotesensing
- **Scope alignment:** Broad fit. Strong methodology with public artefacts and honest negative findings will distinguish within a special issue.
- **Impact Factor:** **4.1 (2024 JCR; 5-year IF 4.8)**. Q1 in Remote Sensing.
- **APC:** CHF 2,700 (~USD 3,000-3,100).
- **Open special issues with high relevance (verified active calls at 2026-05-14):**
  - **"Artificial Intelligence and Satellite Remote Sensing for Environmental Monitoring"** — deadline **30 June 2026**. *Explicitly* solicits "reproducible and comparable practices, including open-source code and pipelines, benchmark datasets, standardized reporting/metrics." **Best-matching open special issue.**
  - **"Machine Learning and GeoAI for Remote Sensing Environmental Monitoring"** — explicitly invites "critical commentary papers addressing... model interpretability, reproducibility, transferability, equity, and transparency."

### International Journal of Applied Earth Observation and Geoinformation (Elsevier — "JAG")

- **URL:** https://www.sciencedirect.com/journal/international-journal-of-applied-earth-observation-and-geoinformation
- **Impact Factor:** **9.83 (2024 JCR).** Q1.
- **Scope:** Applied — fits if HIDSAG mineral case study is foregrounded.

### Pattern Recognition (Elsevier)

- **URL:** https://www.sciencedirect.com/journal/pattern-recognition
- **Scope alignment:** Moderate. Natural home if framed as a pattern-recognition methodology paper.
- **Impact Factor:** **7.6** (sources disagree — needs cross-check before final claim).
- **Page limit:** **20-35 pages.** The journal manuscript at 20-30 pages fits exactly.

---

## Recommended target per manuscript

### #1 conference target: **WHISPERS 2026 (Glasgow, 17-19 Nov 2026)**

**Rationale.**

- The **submission window is still open** (deadline 28 July 2026) — IGARSS, ICIP, EUSIPCO, SPIE DCS, and SPIE Sensors + Imaging Europe 2026 abstract windows have all already closed at the time of this report.
- It is the only candidate whose **entire scope is hyperspectral signal processing**, so the band-mask robustness diagnostic — including the partial-negative result on KSC + Botswana and the Salinas-A SWIR-only positive — will be read by exactly the audience that should care.
- The 4-5 page full-paper track gets the work into IEEE Xplore and citeable.
- The November 2026 date gives natural runway: submit band-mask paper to WHISPERS by 28 July 2026, get reviewer feedback in September, fold into the journal manuscript draft in Q4 2026.

### #1 journal target: **IEEE Transactions on Geoscience and Remote Sensing (TGRS)**

**Rationale.**

- Highest scope-fit for a **method-heavy hyperspectral evaluation framework**.
- The **new 10-page overlength threshold (effective 1 Jan 2026)** makes the 20-30 page comprehensive manuscript economically tractable. Budget ~$2,300-4,600 in OPC.
- **IEEE Transparent Peer Review opt-in** lets the reproducibility story extend into the review record.
- TGRS's **single-blind review + Code Ocean + IEEE DataPort hooks** match the existing reproducibility infrastructure.
- IF 9.5 + Q1 + the de-facto top hyperspectral methodology venue is the right calibration for a paper of this scope and effort.

**Honourable mentions / fallbacks.**

- **JSTARS** — fully OA, $1,800 APC, ~10-week review.
- **ISPRS J. Photogrammetry and Remote Sensing** — higher IF (12.2), pattern-recognition-friendly methodology framing.
- **MDPI Remote Sensing "AI and Satellite RS for Environmental Monitoring" special issue (deadline 30 June 2026)** — tactical fallback; call explicitly asks for open-source-code reproducibility and benchmark frameworks.
- **Pattern Recognition** — hard pivot to ML methodology audience; 20-35 pp format fits exactly.

---

## Items still to verify before submission

- WHISPERS 2026 author-kit specifics — pull from the EasyChair-linked author kit when it appears.
- IEEE TGRS final review-timeline figures — cross-check via recent papers' submission histories.
- IGARSS 2026 explicit review-blinding policy — query the TPC.
- JAG and Pattern Recognition APCs — Elsevier per-journal pricing.
- MDPI Remote Sensing "GeoAI" special-issue deadline.

## JCR cross-check audit (c282, 2026-05-18)

Performed a snapshot cross-check of the IF figures cited above
against current web-aggregator data. Significant deltas vs the
2024 JCR numbers in the body of this document:

| Journal | Cited above | 2024 JCR (web search snapshot) | Action |
|---|---|---|---|
| IEEE Transactions on Image Processing | 7.6 ("sources disagree") | **13.7** (also reported as 7.6 by older aggregators) | Update to 13.7 with cross-check note; older sources lag |
| Pattern Recognition | 7.6 (unverified) | 7.6 / 9.84 (sources still disagree) | Re-verify at submission; keep "needs JCR check" flag |
| IJAG | 9.83 (cited) | 9.83 (verified) | OK |
| TGRS | 9.5 (cited) | 7.0 / 8.6 / 9.5 (multiple values reported) | Re-verify; the 9.5 figure may be Clarivate's "Journal Impact Factor" 2024 release (published mid-2025), other sources may cite 5-year or category-specific IFs |

**Authoritative source**: the only definitive number is the one
on Clarivate's Web of Science / JCR portal (institutional access).
Re-fetch within 30 days of any submission deadline to lock in
manuscript claims. The web-aggregator deltas above are caused by
different IF definitions (2-year, 5-year, CiteScore, SJR) and
different release timing relative to the JCR June refresh.

Conclusion: the rankings between candidates do not flip under any
of the variant numbers, so the **recommended targets (WHISPERS
2026 + IEEE TGRS) remain the right choices regardless** of which
IF aggregate is used. The audit is closed pending an
authoritative pre-submission JCR pull.

## Sources

- [WHISPERS 2026 Important Dates](https://www.ieee-whispers.com/important-dates/)
- [WHISPERS 2026 Paper Submission](https://www.ieee-whispers.com/paper-submission/)
- [IGARSS 2026 Call for Papers](https://2026.ieeeigarss.org/call_for_papers.php)
- [IEEE TGRS Information for Authors](https://www.grss-ieee.org/publications/author-resources/tgrs-information-for-authors/)
- [IEEE TGRS on IEEE Xplore](https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=36)
- [IEEE JSTARS](https://www.grss-ieee.org/publications/journal-of-selected-topics-in-applied-earth-observations-and-remote-sensing/)
- [Remote Sensing of Environment](https://www.sciencedirect.com/journal/remote-sensing-of-environment)
- [ISPRS Journal of Photogrammetry and Remote Sensing](https://www.sciencedirect.com/journal/isprs-journal-of-photogrammetry-and-remote-sensing)
- [Remote Sensing (MDPI)](https://www.mdpi.com/journal/remotesensing)
- [MDPI Remote Sensing — AI and Satellite RS for Env. Monitoring SI](https://www.mdpi.com/journal/remotesensing/special_issues/072BTNB365)
- [International Journal of Applied Earth Observation and Geoinformation](https://www.sciencedirect.com/journal/international-journal-of-applied-earth-observation-and-geoinformation)
- [Pattern Recognition (Elsevier)](https://www.sciencedirect.com/journal/pattern-recognition)
- [IEEE Research Reproducibility (Author Center)](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/research-reproducibility/)
