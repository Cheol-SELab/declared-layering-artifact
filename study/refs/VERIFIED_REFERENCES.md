# Verified references — "Declared Layering as a Revisable Hypothesis"

Checked 2026-10-05. Sources were arXiv abstract and HTML full text, Crossref REST metadata (api.crossref.org, the DOI registry record), Semantic Scholar API, Open Library, PyPI, the GitHub API and repository pages, and Artima (the original CRAP posts). Publisher landing pages on ScienceDirect, ACM DL, and UCL returned HTTP 403 to the fetcher. In those cases the bibliographic fields come from Crossref or Semantic Scholar records for the same DOI.

Status key:
- VERIFIED: the primary record was opened and the fields match.
- PARTIAL: the item exists, but some fields come from secondary sources, or the draft's claim is not supported as written.
- NOT FOUND: the item could not be located.

---

## Part A — uncertain draft items

### A1. SlopCodeBench — VERIFIED (draft number WRONG)
[A1] G. Orlanski, D. Roy, A. Yun, C. Shin, A. Gu, A. Ge, D. Adila, N. Roberts, F. Sala, and A. Albarghouthi, "SlopCodeBench: Benchmarking how coding agents degrade over long-horizon iterative tasks," arXiv:2603.24755 [cs.SE], Mar. 2026.
- Opened: https://arxiv.org/abs/2603.24755 and https://arxiv.org/html/2603.24755. The numbers were checked by grepping the raw HTML.
- Abstract: "Quality degrades across checkpoints, with structural erosion rising in 77% of trajectories and verbosity in 75.5%."
- Abstract: "Compared to 473 open-source Python repositories, agent code is 2.3x more verbose and 2.0x more eroded, and the human repositories degrade less often and by smaller margins across their git histories."
- Sec. 3.3: "Erosion rises in 77% of agent trajectories against 53% of human repositories."
- Appendix (human panel): "Erosion rises in 103 of 196 (53%) repositories." This denominator is the set of repositories with at least five sampled commits, measured first to last.
- Sec. 3.3: "Inside the iteration loop, agents accumulate verbosity roughly 7× faster and erosion 5× faster."
- Definition: "we define erosion as the fraction of the codebase's total complexity mass that resides in high-complexity functions", with mass(f) = CC(f) × √SLOC(f).
- Draft correction:
  - Agent trajectories: 77%, not 80%.
  - Human repositories: 53%, not 55%.
  - The figure 55% in the paper is a different statistic: "55% of these repositories are more verbose post-2024 and 59% are more eroded." That is a pre/post-2024 comparison on 321 repositories, about verbosity, not erosion.
- Caution for the draft: "erosion" here is a complexity-concentration metric. It is not architectural or layer erosion.

### A2. arXiv:2512.04273 — VERIFIED (draft wording misleading)
[A2] T. Slater, "Quantitative analysis of technical debt and pattern violation in large language model architectures," arXiv:2512.04273 [cs.SE], Dec. 2025.
- Opened: https://arxiv.org/abs/2512.04273 and https://arxiv.org/html/2512.04273
- Single author.
- The paper calls itself a "comparative pilot study" of three models, with N = 5 runs per model, each building a Book Lending microservice under Hexagonal Architecture constraints.
- Abstract: "we find that while proprietary models achieve high architectural conformance (0% violation rate for GPT-5.1), open-weights models exhibit critical divergence. Specifically, Llama 3 demonstrated an 80% Architectural Violation Rate, frequently bypassing interface adapters to create illegal circular dependencies between Domain and Infrastructure layers."
- Body: "Claude 4.5 showed a 20% violation rate (n=1/5)"; "Llama 3 exhibited an 80% violation rate (n=4/5)"; GPT-5.1 "maintained 100% purity."
- Limitation stated by the author: "A significant limitation of this pilot study is the size disparity between the proprietary models (≈1T+ parameters) and the open-weights Llama 3 (8B)."
- Draft correction:
  - The 80% applies to one model only (Llama 3 8B), from 4 of 5 runs.
  - GPT-5.1 had 0% and Claude 4.5 Sonnet had 20% (1 of 5).
  - "Up to 80% for weaker models" overgeneralizes from n = 5 for a single model.

### A3. Constraint decay — VERIFIED (cite v2; v1 and v2 differ)
[A3] F. Dente, D. Satriani, and P. Papotti, "Constraint decay: The fragility of LLM agents in backend code generation," arXiv:2605.06445 [cs.SE], v1 May 7, 2026; v2 Sep. 18, 2026. DOI: 10.48550/arXiv.2605.06445.
- Opened: https://arxiv.org/abs/2605.06445, https://arxiv.org/abs/2605.06445v1, and https://arxiv.org/html/2605.06445v2
- Affiliations (v2 HTML): Dente and Papotti are at EURECOM, France; Satriani is at the University of Basilicata, Italy.
- Task set: "80 greenfield generation tasks and 20 feature-implementation tasks spanning eight web frameworks".
- v2 abstract: "Evaluated configurations lose 27.28 points on average in assertion pass rates from baseline to fully specified tasks."
- v1 abstract: "Capable configurations lose 30 points on average in assertion pass rates from baseline to fully specified tasks, while some weaker configurations approach zero."
- v2 body: "The worst case, OpenHands + Qwen3-Coder-Next, loses 45 pp (62% of its L0 score), while the most resilient configuration, OpenHands + MiniMax-M2.5, drops 17 pp."
- Draft correction: cite v2 and write "27.28 percentage points on average across evaluated configurations (assertion pass rate, L0→L3)". The "~30 pp" figure is v1, and it applied only to "capable configurations". The blog/news write-ups still repeat the v1 figure.

### A4. arXiv:2605.06464 — VERIFIED (draft attribution needs care)
[A4] S. Sawada, T. Shirai, Y. Kashiwa, K. Yamaguchi, H. Iwata, and H. Iida, "To what extent does agent-generated code require maintenance? An empirical study," in *Proc. 30th Int. Conf. Evaluation and Assessment in Software Engineering (EASE 2026)*, Glasgow, U.K., Jun. 2026. Also arXiv:2605.06464.
- Opened: https://arxiv.org/abs/2605.06464 and https://arxiv.org/html/2605.06464. The venue is taken from the ACM reference block in the HTML.
- Abstract findings: "(i) AI-generated files receive less frequent maintenance than human-authored code, with updates affecting only a small fraction of file size; (ii) the most frequent modifications to AI code are feature extensions, whereas human updates focus on bug fixes, and (iii) human developers perform the large majority of this maintenance."
- Data: about 1,000 files and about 3,200 changes from 100 repositories (AIDev dataset).
- Modularity/encapsulation: this paper does NOT measure modularity or encapsulation. The only relevant sentence is in its Related Work and is attributed to another paper: "Kravchuk-Kirilyuk et al. reported that while AI-generated code can mimic superficial modular structures, it tends to violate principles that sustain maintainability, such as encapsulation, and introduces hidden dependencies."
- If the draft needs that claim, cite the source directly:
  [A4b] A. Kravchuk-Kirilyuk, F. Graciolli, and N. Amin, "The modular imperative: Rethinking LLMs for maintainable software," in *Proc. 1st ACM SIGPLAN Int. Workshop on Language Models and Programming Languages (LMPL '25)*, 2025, pp. 106–111. DOI: 10.1145/3759425.3763392. This was checked against the Crossref record. The paper text itself was not opened, so the claim's wording is PARTIAL.

### A5. Architecture erosion mapping study — VERIFIED
[A5] R. Li, P. Liang, M. Soliman, and P. Avgeriou, "Understanding software architecture erosion: A systematic mapping study," *J. Softw. Evol. Process*, vol. 34, no. 3, Art. no. e2423, 2022. DOI: 10.1002/smr.2423.
- Opened: the Crossref record for 10.1002/smr.2423 (issued 2022-02-09). Landing page: https://onlinelibrary.wiley.com/doi/abs/10.1002/smr.2423. Preprint: arXiv:2112.10934.

### A6. CRAP metric — VERIFIED (blog posts are the canonical source; no peer-reviewed paper found)
[A6a] A. Savoia, "Pardon my French, but this code is C.R.A.P. (2)," *Artima Weblogs*, Jul. 19, 2007. https://www.artima.com/weblogs/viewpost.jsp?thread=210575
- This is the formula's first definition.
- Text: "my AgitarLabs' colleague, Bob Evans, and I decided to do some research."
- Formula as given: "C.R.A.P.(m) = comp(m)^2 * (1 – cov(m)/100)^3 + comp(m)".

[A6b] A. Savoia, "The code C.R.A.P. metric hits the fan — Introducing the crap4j plug-in," *Artima Weblogs*, Oct. 2, 2007. https://www.artima.com/weblogs/viewpost.jsp?thread=215899
- Text: the creators "use a CRAP score of 30 as the threshold for crappiness."
- The byline on both posts is Savoia alone. Bob Evans is credited as co-developer in the text.
- Suggested citation form: "A. Savoia and B. Evans (crap4j), as described in [A6a]". Or cite A6a with Savoia as sole author.
- NOT FOUND: any peer-reviewed or archival paper by Savoia & Evans.

### A7. Robert C. Martin repositories — VERIFIED (both exist)
[A7a] R. C. Martin, "uml-viewer: Live Quil UML class-diagram viewer driven by EDN," GitHub repository, 2026. https://github.com/unclebob/uml-viewer
- Created 2026-09-13; last push 2026-10-02 (GitHub API). Language: Clojure.
- README: "Dependencies that point from a higher level to a lower level are colored red, in accordance with the Dependency Rule of Clean Architecture."
- README: "Color coding comes from CRAP and mutation metrics."

[A7b] R. C. Martin, "missile-command: Dual-platform Missile Command remake (Clojure/ClojureScript)," GitHub repository, 2026. https://github.com/unclebob/missile-command
- Created 2026-07-25; last push 2026-07-30.
- The README describes an `arch-check` task that "fails if pure core requires hosts, acceptance, or IO libs". It also lists a `bb crap` command.
- Cite both as software with an access date. Pin a commit hash if the paper relies on their content.

### A8. de Oliveira et al. 2019 — VERIFIED (author list differs from the draft's guess)
[A8] M. C. de Oliveira, D. Freitas, R. Bonifácio, G. Pinto, and D. Lo, "Finding needles in a haystack: Leveraging co-change dependencies to recommend refactorings," *J. Syst. Softw.*, vol. 158, Art. no. 110420, Dec. 2019. DOI: 10.1016/j.jss.2019.110420.
- Opened: the Crossref record. The ScienceDirect page returned 403.
- The approach recommends move method and move field refactorings that remove "evolutionary smells" (co-change dependencies across classes). It was evaluated on 49 Java projects with 610 evolutionary smells found; this detail comes from the search snippet of the abstract and should be confirmed from the PDF before quoting.
- Marco Tulio Valente is NOT an author.

### A9. Evolution-aware remodularization (TOSEM) — VERIFIED
[A9] F. Meng, Y. Wang, C. Y. Chong, H. Yu, and Z. Zhu, "Evolution-aware constraint derivation approach for software remodularization," *ACM Trans. Softw. Eng. Methodol.*, vol. 33, no. 8, pp. 1–43, Nov. 2024. DOI: 10.1145/3676960.
- Opened: the Crossref and Semantic Scholar records (DBLP key journals/tosem/MengWCYZ24). The ACM DL returned 403.
- The approach is called "Escort". It derives clustering constraints from architecture differences between versions and from commit history.
- The article number was not exposed in the records consulted, so use pp. 1–43.

---

## Part B — standard references

| # | IEEE-style reference | Opened | Status |
|---|---|---|---|
| B1 | D. L. Parnas, "On the criteria to be used in decomposing systems into modules," *Commun. ACM*, vol. 15, no. 12, pp. 1053–1058, Dec. 1972. DOI: 10.1145/361598.361623 | Crossref | VERIFIED |
| B2 | R. C. Martin, *Clean Architecture: A Craftsman's Guide to Software Structure and Design*. Boston, MA, USA: Pearson (Prentice Hall), 2017. ISBN 978-0134494166 | Open Library (publication date Sep. 10, 2017) | VERIFIED |
| B3 | R. C. Martin, *Agile Software Development: Principles, Patterns, and Practices*. Upper Saddle River, NJ, USA: Prentice Hall, 2002. ISBN 978-0135974445. This is the source for SDP, SAP, CCP, and ADP. | Open Library (Oct. 15, 2002; some printings carry ©2003) | VERIFIED |
| B4 | C. Y. Baldwin and K. B. Clark, *Design Rules, Vol. 1: The Power of Modularity*. Cambridge, MA, USA: MIT Press, 2000. ISBN 978-0262024662 | Open Library | VERIFIED |
| B5 | H. Gall, K. Hajek, and M. Jazayeri, "Detection of logical coupling based on product release history," in *Proc. Int. Conf. Softw. Maintenance (ICSM)*, 1998, pp. 190–198. DOI: 10.1109/ICSM.1998.738508 | Crossref | VERIFIED |
| B6 | T. Zimmermann, P. Weißgerber, S. Diehl, and A. Zeller, "Mining version histories to guide software changes," *IEEE Trans. Softw. Eng.*, vol. 31, no. 6, pp. 429–445, Jun. 2005. DOI: 10.1109/TSE.2005.72 | Crossref and Semantic Scholar. Crossref misorders the authors; Semantic Scholar gives Zimmermann, Weißgerber, Diehl, Zeller, which is the published order. | VERIFIED |
| B7 | G. C. Murphy, D. Notkin, and K. Sullivan, "Software reflexion models: Bridging the gap between source and high-level models," in *Proc. 3rd ACM SIGSOFT Symp. Found. Softw. Eng. (FSE)*, 1995, pp. 18–28. DOI: 10.1145/222124.222136. Also *ACM SIGSOFT Softw. Eng. Notes*, vol. 20, no. 4. | Crossref (the record title is truncated to "Software reflexion models"; the subtitle is standard) | VERIFIED |
| B8 | A. MacCormack, J. Rusnak, and C. Y. Baldwin, "Exploring the structure of complex software designs: An empirical study of open source and proprietary code," *Manage. Sci.*, vol. 52, no. 7, pp. 1015–1030, Jul. 2006. DOI: 10.1287/mnsc.1060.0552 | Crossref | VERIFIED |
| B9 | M. M. Lehman, "Programs, life cycles, and laws of software evolution," *Proc. IEEE*, vol. 68, no. 9, pp. 1060–1076, Sep. 1980. DOI: 10.1109/PROC.1980.11805 | Crossref | VERIFIED |
| B10 | S. Brand, *How Buildings Learn: What Happens After They're Built*. New York, NY, USA: Viking, 1994. ISBN 978-0670835157 | Open Library | VERIFIED |
| B11 | N. Ford, R. Parsons, and P. Kua, *Building Evolutionary Architectures: Support Constant Change*. Sebastopol, CA, USA: O'Reilly Media, 2017. ISBN 978-1491986363 | Open Library | VERIFIED |
| B11b | N. Ford, R. Parsons, P. Kua, and P. Sadalage, *Building Evolutionary Architectures: Automated Software Governance*, 2nd ed. Sebastopol, CA, USA: O'Reilly Media, 2022. ISBN 978-1492097549. Cite the 2nd edition for "fitness functions as automated governance". | Open Library lists 2023; retailer listings give Nov./Dec. 2022. The O'Reilly page returned 403. Use 2022. | PARTIAL (year) |
| B12 | M. Papadakis, M. Kintis, J. Zhang, Y. Jia, Y. Le Traon, and M. Harman, "Mutation testing advances: An analysis and survey," in *Advances in Computers*, vol. 112. Amsterdam, The Netherlands: Elsevier, 2019, ch. 6, pp. 275–378. DOI: 10.1016/bs.adcom.2018.03.015 | Crossref and Semantic Scholar (DBLP journals/ac/PapadakisK00TH19) | VERIFIED |
| B13 | R. A. DeMillo, R. J. Lipton, and F. G. Sayward, "Hints on test data selection: Help for the practicing programmer," *Computer*, vol. 11, no. 4, pp. 34–41, Apr. 1978. DOI: 10.1109/C-M.1978.218136 | Crossref | VERIFIED |
| B14 | A. E. Hassan and R. C. Holt, "Predicting change propagation in software systems," in *Proc. 20th IEEE Int. Conf. Softw. Maintenance (ICSM)*, 2004, pp. 284–293. DOI: 10.1109/ICSM.2004.1357812 | Crossref | VERIFIED |
| B15 | L. L. Silva, M. T. Valente, and M. de A. Maia, "Co-change clusters: Extraction and application on assessing software modularity," in *Transactions on Aspect-Oriented Software Development XII* (LNCS 8989). Berlin, Germany: Springer, 2015, pp. 96–131. DOI: 10.1007/978-3-662-46734-3_3 | Crossref | VERIFIED |
| B15b | L. L. Silva, M. T. Valente, and M. de A. Maia, "Co-change patterns: A large scale empirical study," *J. Syst. Softw.*, vol. 152, pp. 196–214, Jun. 2019. DOI: 10.1016/j.jss.2019.03.014. Optional, more recent alternative. | Crossref | VERIFIED |
| B16 | T. Ball, J.-M. Kim, A. A. Porter, and H. P. Siy, "If your version control system could talk...," in *Proc. ICSE Workshop on Process Modelling and Empirical Studies of Software Engineering*, 1997. | Only ResearchGate and secondary listings. No DOI; no primary proceedings record found. | PARTIAL |
| B17 | D. Beyer and A. Noack, "Clustering software artifacts based on frequent common changes," in *Proc. 13th Int. Workshop Program Comprehension (IWPC)*, 2005, pp. 259–268. DOI: 10.1109/WPC.2005.12 | Crossref | VERIFIED |
| B18 | D. Seddon, "Import Linter," Python package, ver. 2.15. Docs: https://import-linter.readthedocs.io/en/stable/; source: https://github.com/seddonym/import-linter (repository created Jan. 2019). | PyPI JSON (author "David Seddon", summary "Lint your Python architecture") and the docs page. Contract types listed on the docs page: Forbidden, Protected, Layers, Independence, Acyclic siblings, Custom. Cite the version actually used in the study. | VERIFIED |
| B19 | P. Gafert *et al.*, "ArchUnit," TNG Technology Consulting GmbH. https://www.archunit.org/; https://github.com/TNG/ArchUnit | archunit.org: "ArchUnit is a free, simple and extensible library for checking the architecture of your Java code using any plain Java unit test framework." | VERIFIED |
| B20 | T. Fawcett, "An introduction to ROC analysis," *Pattern Recognit. Lett.*, vol. 27, no. 8, pp. 861–874, Jun. 2006. DOI: 10.1016/j.patrec.2005.10.010 | Crossref | VERIFIED |
| B21 | B. A. Nosek, C. R. Ebersole, A. C. DeHaven, and D. T. Mellor, "The preregistration revolution," *Proc. Natl. Acad. Sci. USA*, vol. 115, no. 11, pp. 2600–2606, Mar. 2018. DOI: 10.1073/pnas.1708274114 | Crossref | VERIFIED |
| B22 | E. Kalliamvakou, G. Gousios, K. Blincoe, L. Singer, D. M. German, and D. Damian, "The promises and perils of mining GitHub," in *Proc. 11th Working Conf. Mining Softw. Repositories (MSR)*, 2014, pp. 92–101. DOI: 10.1145/2597073.2597074 | Crossref | VERIFIED |
| B23 | J. Cohen, "A coefficient of agreement for nominal scales," *Educ. Psychol. Meas.*, vol. 20, no. 1, pp. 37–46, 1960. DOI: 10.1177/001316446002000104 | Crossref | VERIFIED |

---

## Part C — additional recent works (all opened)

1. **R. Li, M. Soliman, P. Liang, and P. Avgeriou**, "Symptoms of architecture erosion in code reviews: A study of two OpenStack projects," in *Proc. IEEE 19th Int. Conf. Softw. Archit. (ICSA)*, 2022, pp. 24–35. DOI: 10.1109/ICSA53651.2022.00011. arXiv:2201.01184.
   - Relevance (a): practitioner-side evidence that architecture violations are discussed in review, from 21,274 comments manually checked.
2. **R. Li, P. Liang, and P. Avgeriou**, "Warnings: Violation symptoms indicating architecture erosion," *Inf. Softw. Technol.*, vol. 164, Art. no. 107319, Dec. 2023. DOI: 10.1016/j.infsof.2023.107319. arXiv:2212.12168.
   - Relevance (a): characterizes architecture-violation symptoms in 606 review comments from OpenStack and Qt. Supports framing violations as an erosion signal.
3. **R. Li, P. Liang, P. Avgeriou, and Y. Wang**, "Towards automated identification of violation symptoms of architecture erosion," arXiv:2306.08616 (v6), 2023–2025.
   - Relevance (a/c): ML/DL/LLM classifiers for detecting violation symptoms. The abstract reports SVM+word2vec F1 = 0.808.
4. **L. L. Silva, M. T. Valente, and M. de A. Maia**, "Co-change patterns: A large scale empirical study," *J. Syst. Softw.*, vol. 152, pp. 196–214, 2019. DOI: 10.1016/j.jss.2019.03.014.
   - Relevance (b): co-change clusters as a modularity-assessment signal at scale. Note this is 2019, slightly before the requested window.
5. **F. Meng, Y. Wang, C. Y. Chong, H. Yu, and Z. Zhu**, TOSEM 2024 (A9 above).
   - Relevance (b): history-derived constraints guiding remodularization. This is the closest prior art to history-driven re-layering.
6. **D. Amoroso d'Aragona, L. Pascarella, A. Janes, V. Lenarduzzi, R. Peñaloza, and D. Taibi**, "On the empirical evidence of microservice logical coupling. A registered report," arXiv:2306.02036, 2023.
   - Relevance (b): logical coupling as an architecture metric, using a registered-report design. That design is a methodological precedent for preregistration.
7. **A. Canedo**, "Architecture as capability equalizer for coding agents," arXiv:2608.21747, Aug. 2026.
   - Relevance (c/d): a controlled experiment with 90 trials and 6 models. It compares architecture-specification formats, including "TypeScript interface contracts with ArchUnit-style rules". The abstract reports a "strong format x model interaction".
8. **R. K. Sharma**, "ContextCov: Deriving and enforcing executable constraints from agent instruction files," arXiv:2603.00822 (v2), 2026.
   - Relevance (c/d): compiles AGENTS.md architectural boundaries into executable checks. The abstract reports 88.3% constraint compliance vs. 67.0% and 50.3% baselines (300 tasks, 12 repositories, SWE-bench Lite).
9. **W. Yang, R. He, and M. Zhou**, "A first look at coding agents' compliance with AI contribution rules in open-source communities," arXiv:2607.26819, Jul. 2026.
   - Relevance (c): agents' adherence to declared repository rules (106 issues, 49 repositories). It concerns process rules, not architecture rules.
10. **A. Kravchuk-Kirilyuk, F. Graciolli, and N. Amin**, LMPL '25 (A4b above). DOI: 10.1145/3759425.3763392.
    - Relevance (c): position paper arguing that LLM code mimics modular structure but violates encapsulation. Only metadata was opened.

Not peer-reviewed, but directly adjacent (e); cite only as software or gray literature, with caution:
- **H. Lee (hslee16)**, "Archy: Architectural sensor for Python codebases," GitHub, created 2026-05-09. https://github.com/hslee16/Archy
- It wraps import-linter contracts. Its README reports author-run measurements:
  - "151 commit pairs in projects that declare an architecture" with "0.66% per commit" contract violations.
  - "107 samples of those same projects over time" found "null on all four pre-registered signals" for rules going stale.
  - "25 live agent runs on the riskiest SWE-bench tasks" with 0% declared-layer violations.
- It has an advisory co-change command, `archy coupling`, which finds module pairs that co-change without an import edge. It does not revise layers from history.
- This is the closest existing tool to the paper's thesis and should be acknowledged or differentiated.
- (e) NOT FOUND: no peer-reviewed empirical study of import-linter usage was found.
- (d) NOT FOUND: no peer-reviewed empirical study of fitness functions was found. arXiv:2509.10085 (Zech & Pekaric, "Sustaining research software: A fitness function approach", 2025) is a proposal, not an empirical study.
