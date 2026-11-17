# Bogotá Population Model: Project Plan

Nov 14, 2026 · Gregorio Maya

## Purpose and scope

Build an open, reproducible model that estimates resident population for every cadastral lot in Bogotá, refreshed once per cadastral vigencia, and published at block (manzana) and H3 level. The research found no existing product that meets all four requirements (building resolution, frequent updates, reuse, scenarios), so the plan builds one on census + cadastre + official projections.

**v1 is done when:**

- A single command rebuilds a 2026 population estimate per lot from raw downloads, with no manual steps.
- Lot totals sum exactly to the DANE–SDP post-COVID projection for each UPZ/UPL.
- A back-cast to 2018 is scored against CNPV 2018 at block level, and the MAPE/RMSE are published in the repo.
- Outputs are released as GeoParquet at block and H3 resolution under an open licence, with a methods page anyone can follow.

**Out of scope for v1:** daytime population, the metropolitan region outside Bogotá D.C., rural disperso areas (39.5% census omission makes them a separate problem), and age/sex breakdowns below UPZ. Each is listed in the parking lot at the end.

&#91;embedded content: roadmap · phases 0–6, about 4 months to v1.0\]

Phases 0–3 run in sequence; validation and publication start with the MVP and repeat on every release after it.

## Decisions

All eight were closed on 14 Nov 2026. In Phase 0 each becomes an ADR in docs/decisions/.

| # | Decision | Chosen | Why it matters |
| --- | --- | --- | --- |
| D1 | Code licence | MIT | Lowest friction for public-sector clients and other researchers reusing the pipeline |
| D2 | Output data licence | CC BY 4.0 | Matches Datos Abiertos Bogotá and DANE terms, so attribution chains stay clean |
| D3 | Main language | Python (geopandas, DuckDB, tobler) | One stack keeps CI, packaging and contributors simple |
| D4 | Repo language | Code and issues in English; README and methods page in English and Spanish | Spanish reaches SDP, UAECD and local academia; English reaches the dasymetric literature |
| D5 | Repo home | Personal GitHub account (gregmaya) | GitHub redirects after a transfer, so moving to an org later costs little |
| D6 | Public granularity | Block + H3 public; lot level private | In single-family lots a modelled count is close to revealing household size, which DANE itself suppresses for 1–3 dwellings |
| D7 | Where outputs live | GitHub Releases per version + Zenodo DOI for major releases | A Release is a tagged snapshot of the repo with files attached. Zenodo, once linked to the repo, archives each Release automatically and gives it a citable DOI |
| D8 | Control total | DANE–SDP post-COVID projections (2025 release) | The candidate totals disagree (7.9 M vs 7.5 M); one official control, documented, avoids arguments later |

## Working model: public, documented, technical

The GitHub repo is the single source of truth. Code, methods, decisions and issues live there; data does not.

**Public.** The repo is public from the first commit. Raw downloads are never committed; a manifest (URL, vigencia, download date, SHA-256) is. Anyone with the repo and an internet connection can rebuild every output.

**Documented.** Three layers, each with a different reader:

1. `README` (EN/ES): what the dataset is, how to download it, how to cite it.
2. A methods site built with MkDocs or Quarto and published on GitHub Pages: data sources, the dasymetric logic, validation results, known biases.
3. Architecture Decision Records in `docs/decisions/`: one short markdown file per choice (D1–D8 above become ADR-0001 to ADR-0008). Future-you and reviewers can see why, not just what.

**Technical.** Every number in the methods page is produced by code in the repo. Tests run in GitHub Actions on a small sample (one UPZ) so CI stays fast. Each release is tagged with the cadastral vigencia it uses, for example `v2026.1`.

**When to move to VS Code.** The moment D1–D8 are closed. Phase 0 is creating the repo, the environment and the first download scripts, and that work belongs in VS Code with Claude Code alongside, not in chat. Until then, this doc is where the plan evolves. After the move, this doc gets frozen and its content becomes `docs/plan.md` and the ADRs.

## Repository structure and stack

The layout separates what is downloaded, what is derived and what is published, so a new vigencia only re-runs the stages it touches. Working name: `bogota-pop` (to confirm).

```
bogota-pop/
├── README.md / README.es.md
├── LICENSE (code) · DATA_LICENSE (outputs)
├── CITATION.cff
├── pyproject.toml            # pixi or uv lockfile alongside
├── config/
│   ├── sources.yaml          # every dataset: URL, vigencia, licence, checksum
│   └── model.yaml            # weights, thresholds, control year
├── src/bogota_pop/
│   ├── ingest/               # one module per source (dane, uaecd, sdp, em)
│   ├── harmonise/            # CRS, geometry repair, MGN↔cadastre matching
│   ├── model/                # dasymetric (MVP), housing-unit (v2), scenarios
│   ├── validate/             # back-cast, EM 2025, Movilidad 2023
│   └── publish/              # aggregation to block/H3, privacy rules
├── pipeline/                 # Snakefile: the DAG (ADR-0010)
├── notebooks/                # exploration only; never a pipeline step
├── tests/                    # unit + one-UPZ integration test
├── docs/
│   ├── methods/              # MkDocs/Quarto site
│   └── decisions/            # ADRs
└── data/                     # git-ignored: raw/ interim/ processed/
```

| Layer | Tool | Note |
| --- | --- | --- |
| Environment | pixi (conda-forge) or uv | pixi handles GDAL/PROJ cleanly; uv is faster if wheels suffice |
| Geometry | geopandas, shapely 2, pyogrio | GeoParquet as the internal format |
| Analytics | DuckDB with the spatial extension | Handles \~3 M predios against tens of thousands of blocks on a laptop |
| Areal / dasymetric | tobler (PySAL) | Reference implementation to compare against our own weights |
| Grid output | h3-py | Resolution 9 (\~0.1 km²) and 10 to decide in Phase 6 |
| Orchestration | Snakemake (ADR-0010) | Re-runs only stages whose inputs changed |
| Quality | ruff, pytest, pre-commit, GitHub Actions | CI on one UPZ sample |
| Docs | MkDocs Material or Quarto | Quarto if methods pages should embed live maps and figures |
| CRS | MAGNA-SIRGAS Origen Nacional (EPSG:9377) | DANE and UAECD both publish in or convert cleanly to it |

## Phase 0: Bootstrap (about 1 week, in VS Code)

Goal: an empty but working repo where `snakemake` runs, tests pass and CI is green.

- [x] Close D1–D8 and write them as ADR-0001 to ADR-0008
- [x] Create the public repo with licence files, `CITATION.cff`, `.gitignore` for `data/`, issue and PR templates
- [x] Lock the environment (pixi or uv) and confirm GDAL, PROJ and DuckDB spatial install on macOS and in CI
- [x] Scaffold `src/bogota_pop/` as an installable package with a CLI entry point (`bogota-pop ingest`, `model`, `validate`, `publish`)
- [x] Set up ruff, pytest, pre-commit and a GitHub Actions workflow
- [x] Write `config/sources.yaml` with every dataset from the research inventory, even ones not used until later
- [x] Open GitHub milestones for Phases 1–6, each with one or two issues whose checklists cover the tasks below (English and Spanish, ADR-0011)
- [x] Tag `v0.0.1` when the exit gate passes (a git tag only, no GitHub Release: Releases are for data versions, ADR-0007)
- [x] Copy this plan into `docs/plan.md`

**Exit gate:** CI green on an empty pipeline; a stranger can clone and run `bogota-pop --help` in under 10 minutes.

## Phase 1: Data acquisition and inventory (1–2 weeks)

Goal: every source used in v1 downloads by script, lands as GeoParquet in EPSG:9377 and has a one-page profile in the docs.

| Priority | Dataset | Used for | Check on arrival |
| --- | --- | --- | --- |
| Core | [DANE MGN integrado CNPV 2018](https://geoportal.dane.gov.co/descargas/mgn-integrado/), manzana layer | 2018 population per block (TP27\_PERSO), dwellings (TVIVIENDA) | Blocks with dwellings but 0 persons (DATO\_ANM is not a flag); block total plus clase level vs 7,181,469 censused (clase layer) |
| Core | UAECD Lote, Construcción, Manzana, Uso, Predio (Datos Abiertos Bogotá), monthly cut October 2026 | Residential area, floors, PH units per lot (units come from Predio; Uso has no unit counts) | Vigencia date; share of lots with residential use; PH vs NPH counts (both need UAECD's code dictionary) |
| Core | [DANE–SDP projections 2005–2035](https://datosabiertos.bogota.gov.co/dataset/proyecciones-y-retroproyecciones-de-poblacion-2005-2035) by UPZ/UPL | Annual control totals | UPZ sum equals city total; 2024 ≈ 7,929,539 |
| Core | UPZ and UPL boundaries (SDP) | Control geography | Topology; coverage of all blocks |
| v2 | [SDP licencias, capa geográfica](https://datosabiertos.bogota.gov.co/dataset/licencia-bogota-d-c) | New units since 2018 | Join rate to lot codes |
| v2 | [DANE–SDP proyecciones de hogares y viviendas](https://datosabiertos.bogota.gov.co/en/dataset/proyecciones-de-hogares-y-viviendas-2018-2035) | Household size trend | Matches population projection base |
| Validation | Encuesta Multipropósito 2025 microdata | Independent population and households by UPL | Weights and UPL codes |
| Validation | Encuesta de Movilidad 2023, ZAT shapefile | Population by ZAT | Total 7.5 M vs control, documented gap |
| Validation | CNPV 2018 microdata (11\_Bogota.zip) | Rebuild counts for anonymised blocks if allowed | Licence terms for derived outputs |
| Comparison | WorldPop, GHS-POP, Meta HRSL | Benchmark only | Same CRS and aggregation |
| Scenarios | POT Decreto 555 tratamientos and edificabilidad | Phase 5 | Layer names and attributes |

Tasks:

- [ ] One ingest module per source, with checksum and vigencia recorded in a `manifest.json`
- [ ] Pin the cadastral vigencia (2026 base, plus 2018 for the back-cast) and confirm older vigencias are still downloadable
- [ ] Compare the two licence datasets (SDP capa geográfica vs curadurías' licencias ejecutoriadas): what each covers, join rate to lot codes, completion dates; keep one or both for Phase 3
- [ ] Write a data profile page per source: fields used, row counts, known issues
- [ ] Request any non-public data (older cadastral vigencias, if not online) through a formal derecho de petición early, since replies can take weeks
- [ ] Etapas layers for Phase 1 (ADR-0013): PMTiles writer, `config/etapas.yaml`, `etapas.json`, privacy check; first layers MGN blocks, MGN clase, UAECD blocks

**What is online for the cadastre (checked 2026-11-15).** UAECD publishes a monthly cut of each dataset. The 2026 base is the October 2026 cut (`vigencia: "2026-10"` for all five `uaecd_*` sources). Nothing from 2018 is online: the oldest cuts are December 2019 (Predio), March 2020 (Uso) and December 2022 (Lote, Construcción, Manzana). The MVP does not need 2018 cadastre: it spreads 2018 block counts over the 2026 lots and scales to the 2026 projections. 2018 cadastre matters for the back-cast (Phase 4) and the Phase 3 calibration. Until a derecho de petición brings it, the fallback is 2019–2020 weights (Predio and Uso tables joined to today's lots by lot code), plus a same-year spatial test (hide each block's count, rebuild it from its section, compare). The petition is still worth sending, but it no longer blocks anything.

**Exit gate:** `bogota-pop ingest` rebuilds `data/raw` and `data/interim` from nothing, and the profiles answer the three unverified questions from the research (how many blocks are anonymised, whether 2018 cadastre is available, the IDOM/ODUR layer's licence). The 2018 and anonymised block layers are reviewed in Etapas.

## Phase 2: MVP, census-to-lot dasymetric model (2–4 weeks)

Goal: a 2026 population estimate per lot, built with CEDS-style logic (Maantay et al., 2007) and controlled to official UPZ totals. This is release `v0.1`.

1. **Resolve anonymised blocks.** Anonymised blocks have no own count: they show 0 persons (DATO\_ANM does not flag them, see the glossary). Pool their population at the section level and redistribute by cadastral residential weight. *To revisit:* the clase layer shows no household people missing from cabecera blocks (open question Q2), so this step may only concern LEA residents and centro poblado.
2. **Match MGN blocks to cadastral blocks.** Codes differ, so match by geometry: intersect, keep pairs above an overlap threshold (start at 50% of the smaller polygon, tune it), and split 1:n cases by residential area. Log every unmatched block.
3. **Compute a residential weight per lot.** PH lots use the count of residential predios (units). NPH lots use residential built area from the Uso table, split into the ≤3 and ≥4 floor categories. Mixed-use lots count only the residential share.
4. **Distribute block population to lots** in proportion to the weight.
5. **Scale to the target year** so lot totals in each UPZ equal the DANE–SDP projection. This absorbs the 3.1% census omission and post-2018 growth.
6. **Write outputs** to `data/processed/` with a version tag and run log.

```latex
P_{l,t} = P_{b,2018} \cdot \frac{w_l}{\sum_{k \in b} w_k} \cdot \frac{P^{proj}_{u,t}}{\sum_{l \in u} P_{l,2018}^{*}}
```

where l is a lot, b its 2018 block, u its UPZ, w the residential weight and P\* the step-4 estimate.

Known weakness of the MVP: it freezes 2018 geography. A tower finished in 2023 gets people only if its lot already had residential weight in the chosen vigencia and its block had census population. Phase 3 fixes this.

**Exit gate:** the pipeline runs end to end; UPZ totals match the projections exactly; a first map of the result is reviewed by eye against satellite imagery in three contrasting UPZ (a dense PH area, a consolidated low-rise barrio, a peripheral informal edge). Match and MVP layers are reviewed in Etapas.

## Phase 3: Annual update engine, housing-unit method (6–8 weeks)

Goal: replace "2018 population redistributed" with "dwellings that exist this vigencia × occupancy × people per household", so new buildings get people and demolished ones lose them. This is release `v1.0`.

```latex
P_{l,t} = U_{l,t} \cdot o_{g} \cdot h_{g,t} \quad \text{then raked to } P^{proj}_{u,t}
```

U = dwelling units on lot l in vigencia t; o = occupancy rate and h = persons per occupied household, both for group g (estrato × typology × UPZ).

1. **Dwelling stock per lot and vigencia.** PH: count residential predios directly. NPH: estimate units from residential area divided by a typical unit size per estrato and floor class, calibrated in step 2.
2. **Calibrate against 2018.** Fit o and h by group using the 2018 cadastral vigencia and CNPV 2018 block counts. Keep the parameters in `config/model.yaml` with their fit statistics.
3. **Trend h forward.** Use the DANE–SDP household projections and EM 2021 → 2025 to move household size by year; keep o fixed unless EM shows a change.
4. **Add the licence layer.** Lots with a completed licence after the vigencia date get provisional units, flagged as such, so the estimate is not a year behind the cadastre.
5. **Rake to official totals** by UPZ/UPL, as in Phase 2.
6. **Make it annual.** A new vigencia is a config change plus `bogota-pop run --vigencia 2027`; diff the outputs against the previous release and publish a change log by UPZ.

**Exit gate:** the 2026 run beats the MVP on the Phase 4 back-cast metrics; re-running with only the vigencia changed produces a clean release with no code edits. The v1 layer is compared with the MVP layer in Etapas.

## Phase 4: Validation (runs alongside Phases 2 and 3)

Validation starts with the MVP, not after v1. Every release carries the same scorecard so improvements are measured, not asserted.

| Test | Truth | Unit | Metrics | Notes |
| --- | --- | --- | --- | --- |
| Back-cast 2018 | CNPV 2018 | Block | MAPE, RMSE, error by density quintile | Model 2018 from the 2018 vigencia, hide the block counts, compare. The main test |
| Leave-UPZ-out | CNPV 2018 | Block | Same | Calibrate parameters without one UPZ, predict it; guards against overfitting in Phase 3 |
| EM 2025 | Encuesta Multipropósito | UPL, UTIEM | % error in population and households | Independent of the census; the best check of 2025–26 estimates |
| Movilidad 2023 | Encuesta de Movilidad | ZAT | Rank correlation, % error | Different total (7.5 M), so compare shares, not counts |
| Benchmarks | WorldPop, GHS-POP, HRSL | Block, H3 | Same as back-cast | Shows the gain over global grids; useful for the methods page |
| Eyeball | Satellite imagery, street view | Sample of 100 lots | Pass/fail | Catches gross errors metrics miss (car parks, churches with people) |

- [ ] Write the scorecard as code in `validate/`, output a markdown table into the docs on each run
- [ ] Set a target before seeing results: for example, block-level MAPE below the MVP's, and no density quintile worse than the MVP
- [ ] Map residuals; clusters in the periphery or in inquilinato areas point to the informality and migration biases below

**Exit gate:** the scorecard is published in the methods site and regenerates automatically; the residuals layer is public in Etapas.

## Phase 5: Scenarios (after v1.0, 3–4 weeks)

Goal: answer "how many people would live here in year X if Y happens" with the same engine, by changing U (units) and h (household size) instead of the population directly.

Three scenario types, in order of build:

1. **Pipeline.** Licences granted but not yet in the cadastre become units over a 2–3 year completion lag. Closest to a forecast.
2. **POT build-out.** Lots under renovation or development treatments in Decreto 555 receive units up to a share of permitted edificabilidad (25%, 50%, 100% as parameters). An envelope, not a prediction.
3. **Custom.** A user-supplied GeoPackage of projects (lot, units, year) for client work, such as testing a transit corridor or a plan parcial.

Each scenario is a YAML file in `scenarios/`, versioned in git, so a result can always be traced to its assumptions. Outputs keep official UPZ totals as an optional constraint: on for redistribution questions, off for growth questions.

**Exit gate:** two documented example scenarios in the methods site, each reproducible from its YAML.

## Phase 6: Publication and releases

Goal: each version is a citable dataset that other projects can pull with one line of code.

- [ ] Aggregate lot estimates to block and H3 (resolution chosen after testing 9 vs 10 for disclosure risk)
- [ ] Apply privacy rules before export: suppress or merge units with fewer than a threshold of dwellings (mirror DANE's 1–3 dwelling rule), round counts
- [ ] Package GeoParquet + GeoPackage + a CSV keyed by block code, with a data dictionary, plus a PMTiles file and a UPZ/UPL summary JSON for the viewer
- [ ] Tag the release (`v2026.1`), attach files to GitHub Releases, mint a Zenodo DOI for majors
- [ ] Publish a small web map on GitHub Pages so non-technical users can explore without downloading
- [ ] Write a short methods note in Spanish for SDP/UAECD and a preprint-style write-up in English for the methods literature
- [ ] Add a `CHANGELOG.md` entry with what changed in data, method and results

**Release rhythm:** one release per cadastral vigencia (early each year, after UAECD publishes), plus interim releases when DANE–SDP revise projections or EM microdata appear.

**Reuse in other projects:** a small loader, `bogota_pop.load(level="block", year=2026)`, so movilidad, accessibility or equipment analyses import a pinned version instead of copying files around.

## Parallel track: online viewer (separate repo)

The viewer lives in its own repo (working name `bogota-pop-viewer`) with its own environment, and treats the model repo as a data provider. It never imports the Python package; it only reads published, versioned files.

**Data contract between the two repos.** The model repo's Phase 6 adds one more output per release: vector tiles of block and H3 results, built with tippecanoe into a single PMTiles file, plus a small JSON of UPZ/UPL summaries. The viewer pins a release tag (`v0.1`, `v1.0`) in its config, so a new model release never breaks the live site until the viewer is bumped on purpose.

**It can start early.** Once Phase 1 lands, the CNPV 2018 block layer is real, public data with the same geometry the model will publish. The viewer can be built against it while Phases 2–3 run, then switch to `v0.1` when it exists.

**Viewer decisions (closed 14 Nov 2026):**

| # | Decision | Chosen |
| --- | --- | --- |
| V1 | Stack | Static site: Vite + MapLibre GL JS + PMTiles |
| V2 | Where tiles are hosted | GitHub Pages in the viewer repo while the PMTiles file stays well under the 100 MB file limit; Cloudflare R2 if it grows. Range requests and CORS tested in the viewer's Phase 0 |
| V3 | First version's scope | Block choropleth, H3 toggle and UPZ panel for v0.1; year slider once two releases exist; scenarios after model Phase 5 |
| V4 | UI language | Spanish only (the model repo's docs stay bilingual per D4) |
| V5 | Domain | gregmaya.github.io/bogota-pop-viewer |

- [ ] Write V1–V5 as ADRs in the viewer repo
- [ ] Add a PMTiles + summary JSON step to the model repo's Phase 6 checklist
- [x] Create the viewer repo empty alongside the model repo
- [ ] Start building the viewer: generic Etapas mode against a fixture `etapas.json` first, then the real Phase 1 layers (ADR-0013; kickoff prompt in `docs/companion/viewer-kickoff.md`)

### Etapas mode: every stage on the map

Each model stage writes its own PMTiles next to its regular output, so progress is reviewed on a map, not only in metrics. The viewer gets a second mode, "Etapas", with a layer switcher across them. The real list of layers is `config/etapas.yaml`, and the viewer draws whatever its `etapas.json` lists (ADR-0013); the table below is a summary.

| Stage layer | Produced in | Level | Public |
| --- | --- | --- | --- |
| CNPV 2018 blocks as downloaded | Phase 1 | Block | Yes |
| Blocks with dwellings but 0 persons (unexplained) | Phase 1 | Block | Yes |
| MGN↔cadastre match, unmatched blocks highlighted | Phase 2 | Block | Yes |
| Residential weight per lot | Phase 2 | Lot | No, local only |
| MVP estimate, 2026 | Phase 2 | Lot (local), block and H3 (public) | Block and H3 only |
| Housing-unit estimate, v1 | Phase 3 | Lot (local), block and H3 (public) | Block and H3 only |
| Back-cast residuals vs CNPV 2018 | Phase 4 | Block | Yes |
| Scenario deltas | Phase 5 | Block and H3 | Yes |

- Development tiles ship as GitHub pre-releases tagged by date (`dev-2026-12-01`). Etapas follows the latest pre-release; the public map stays pinned to the official release.
- Lot-level layers never leave your machine: run the viewer with `npm run dev` pointed at local tiles in `data/processed/`.
- Every phase's exit gate includes reviewing its stage tiles in Etapas.
- The viewer's first real milestone moves up to model Phase 1, with the 2018 and anonymised block layers.

## Risks, known unknowns and parking lot

| Risk | Effect | Mitigation |
| --- | --- | --- |
| MGN↔cadastre block matching is messy | Population lands on the wrong lots | Geometry match with logged thresholds; manual review of the worst 1% |
| 2018 cadastral vigencia not downloadable (**confirmed 2026-11-15**: oldest online is Dec 2019) | No clean back-cast, weak Phase 3 calibration | Request it from UAECD; meanwhile back-cast with Dec 2019 Predio and Mar 2020 Uso joined to today's lots by code (Phase 1 note) |
| Informal growth missing from the cadastre (Usme, Ciudad Bolívar, Bosa edges) | Undercount at the periphery | Flag lots; later test Google Open Buildings 2.5D Temporal as a growth signal |
| Venezuelan migration (591,462 in Bogotá, Dec 2024) concentrated in rentals and inquilinatos | Spatial bias the raking cannot fix | Document as a limitation; examine EM 2025 by UPL for a correction factor |
| Census omission (3.1%) not spatially located | Proportional spread may underweight periphery | Treat as a parameter; test alternative spreads in validation |
| Disclosure at lot level | Ethical and legal exposure | Lot level stays private (D6); privacy rules in Phase 6 |
| Sources change format or URL between vigencias | Pipeline breaks silently | Schema checks at ingest; CI fails loudly |
| Projections revised mid-year | Release out of step with official numbers | Control year and projection release recorded in each version |

**Parking lot (not in v1, revisit later):**

- Daytime population from non-residential uses + school enrolment, or purchased mobile-phone data
- Age and sex structure below UPZ
- Extension to the 20+ municipalities of the Región Metropolitana
- Random-forest layer (popRF) with GHSL, Open Buildings and night lights as covariates, if Phase 4 shows systematic residuals
- Administrative data (SISBÉN, utility subscribers) through a convenio with the Distrito
- DANE's Registro Estadístico Base de Población, if it becomes available below municipality

**Open questions from Phase 1 (raised 2026-11-15, decide before Phase 2 closes):**

- **Q1. Bogotá's edge.** A model that stops at the city limit gives network and accessibility analysis a hard edge: catchments that cross into Soacha, Chía, Cota, Funza, Mosquera or La Calera see no population on the far side. Ideas so far:
  - The MGN file is already national; only the ingest filter (`DPTO_CCDGO = '11'` in `ingest/dane_mgn.py`) limits it. Turn the filter into a list of municipality codes in config when this is decided.
  - Outside Bogotá there is no UAECD cadastre. A second, coarser tier could spread census block counts with building footprints (Google Open Buildings, Microsoft) and control to DANE municipal projections. The output would say which tier each cell came from.
  - This makes the parking-lot item "Extension to the Región Metropolitana" concrete, as a ring of municipalities first.
- **Q2. People not in any block.** In Bogotá, 7,136,912 people are in census blocks (sum of `TP27_PERSO`) against 7,181,469 censused (sum of `STP27_PERS` in the clase layer). The clase layer shows where the 44,557 difference sits (figures in `config/manifest.json`):
  - 31,929 live in group quarters (LEA, `STPERSON_L`): 31,807 in the cabecera, 122 in rural disperso.
  - 12,573 household people live in rural disperso (clase 3), which has no blocks.
  - 55 household people in centro poblado (clase 2) are missing from its blocks (2,525 against 2,470).
  - In the cabecera, household people in blocks equal the clase figure exactly (7,134,442). No household people are missing there, so the 254 blocks with dwellings but 0 persons are not hiding anyone. What they are is still open.

  Leaving the LEA residents out is worse than it looks: the control totals include them, so raking would push them into ordinary homes. Ideas so far:
  - LEA residents: find the lots that hold LEAs (cadastre use codes, OpenStreetMap tags for prisons, barracks, care homes) and spread by capacity. For prisons, INPEC publishes the population of each establishment. Each new source goes into `sources.yaml` first.
  - Rural disperso is out of scope for v1 (glossary), but its 12,573 people are in the control totals too. Decide whether to place them or take them out of the control.
  - The 55 centro poblado people: spread over that clase's blocks by dwellings.
  - Each of these is a method decision for an ADR before it is coded.

## Sources

- [MGN integrado CNPV 2018, instructivo de uso (DANE)](https://geoportal.dane.gov.co/descargas/mgn-integrado/MGN2018_Integrado_CNPV2018_InstructivoUso.pdf)
- [Omisión censal CNPV 2018 (DANE)](https://www.dane.gov.co/files/censo2018/informacion-tecnica/cnpv-2018-omision-censal.pdf)
- [Proyecciones de población post-COVID (SDP)](https://www.sdp.gov.co/gestion-estudios-estrategicos/informacion-estadisticas/censo-2018-post-covid-19/proyecciones-de-poblacion)
- [Uso dataset (UAECD, Datos Abiertos Bogotá)](https://datosabiertos.bogota.gov.co/dataset/uso)
- [Licencias ejecutoriadas curadurías](https://datosabiertos.bogota.gov.co/dataset/licencias-ejecutoriadas-curadurias-bogota)
- [Maantay, Maroko and Herrmann (2007), CEDS](https://www.lehman.edu/media/School-of-Natural-and-Social-Sciences/EGGS-department/document/2007_CaGIS_Maantay_Maroko_Herrmann.pdf)
- [popRF (WorldPop)](https://github.com/wpgp/popRF)
- [Migración Colombia, venezolanos en Colombia, dic. 2024](<https://nexusmigracion.cancilleria.gov.co/sites/default/files/documentos/2026-03/Salud_migrantes_venezolanos_Dic%20(2024)_Migracion_Colombia.pdf>)
