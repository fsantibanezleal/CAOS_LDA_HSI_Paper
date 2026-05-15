# Bibliography — verification protocol

`refs.bib` is the single source of truth for citations across both
manuscripts.

## Verification rules

1. **Every entry must resolve to a publisher record.** A DOI must
   land on the canonical landing page; an arXiv ID must yield the
   cited title/authors; a dataset URL must serve the named dataset.
2. **Group by thematic section** in the .bib file so a reviewer can
   audit the bibliography by topic (LDA theory, neural topic models,
   hyperspectral, datasets, evaluation, infrastructure).
3. **Datasets** carry a `@misc` entry with explicit version + URL so
   the canonical reference is unambiguous.
4. **No fabrication.** If an entry cannot be verified, mark it with
   `note = {Placeholder; verify before submission}` and the
   manuscripts must avoid citing it until verified.

## Categories present

| Section | Topic | Count |
|---|---|---|
| §1 | LDA + topic models foundational theory | 6 |
| §2 | Neural topic models | 5 |
| §3 | LDA on hyperspectral imagery | 2 |
| §4 | Hyperspectral classification / unmixing | 6 |
| §5 | Datasets (Indian Pines, Salinas, Pavia U, KSC, Botswana, HIDSAG) | 6 |
| §6 | Topic-model evaluation (coherence, ARI, Hungarian, stability) | 5 |
| §7 | Spatial segmentation (SLIC, Felzenszwalb) | 2 |
| §8 | Reproducibility + scientific Python infrastructure | 5 |

Total: **37 entries**.

## Open verification tasks before submission

- ✅ **HIDSAG citations resolved 2026-05-15.** Two entries now ship:
  `hidsag2023` (the canonical Scientific Data paper, Ehrenfeld et al.
  2023, doi:10.1038/s41597-023-02061-x) and `hidsag2023figshare`
  (the figshare Collection at doi:10.6084/m9.figshare.c.5983921.v1).
  Felipe Santibáñez-Leal is a co-author of the Scientific Data paper.
  Both manuscripts (conference + journal) and supplement E cite the
  paper; supplement E additionally cites the figshare data release.
- Cross-check IF figures cited in `venues/venue-research.md`
  against the latest JCR.
