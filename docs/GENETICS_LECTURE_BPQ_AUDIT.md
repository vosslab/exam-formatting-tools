# Genetics lecture and BPQ audit

Date: 2026-10-13. BPQ expansion follows the current course. The historical exam audit provides
examples of reasoning; current lecture exercises and the instructor's decisions establish relevance.
See [GENETICS_EXAM_BPQ_AUDIT.md](GENETICS_EXAM_BPQ_AUDIT.md) for the exam ledger and BPQ source map.

## Findings and revised priorities

The strongest additions are individual pedigree genotype/carrier inference, explicit conditioning
on phenotype, Z-linked lethal crosses, and unequal successful-gamete probabilities. A selected-plant
probability generator already exists outside the genetics task lists and is a useful reuse candidate.
Current slides also support a small tetrad-classification task and Drosophila X:autosome reasoning.

The lecture comparison changes three earlier exam-led recommendations:

- Current mixed-inheritance examples use **autosomal dominant plus X-linked recessive**, which BPQ
  already implements. The 2025 exam's AR + XLR carrier/grandson story remains an archival example.
- Incomplete dominance and epistasis appear as separate lecture exercises. The combined
  `3:6:3:4` exam model does not become a current BPQ priority from the exam alone.
- Robertsonian slides define the fusion and its chromosome-21 association. They do not show the
  proposed gamete-to-zygote dosage calculation. Reciprocal-translocation product reasoning is the
  directly supported extension, if needed.

## Teaching evidence and precedence

Source roots supplied by the instructor:

```text
/Users/vosslab/Documents/teaching/CLASS/biol_351-genetics/2025-Genetics-2fall/LECTURES-2025-351genetics/
/Users/vosslab/Documents/teaching/CLASS/biol_351-genetics/2026-Genetics-2fall/LECTURES-2026-351genetics/
```

Use the instructor's explicit inclusion/exclusion decisions first, then 2026 maintained material,
then 2025 current-unit material for later-course topics without a maintained 2026 successor.
Historical exams supply examples after that scope decision. A file's presence, year, or title does
not prove it was delivered or assessed. Slide exercises demonstrate a stronger teaching connection
than an isolated definition or inherited background slide.

| Source set | Material reviewed | Use in this audit |
| --- | --- | --- |
| 2025 `Current-Unit_1-2025/` and `Current-Unit_2-2025/` | 61 instructional PDFs, 2,417 pages; 58 paired ODPs, 2,404 slides; three PDF-only files | Last complete maintained course material; later-unit candidates remain provisional for 2026 |
| 2026 `Current-Unit_1-2026/` plus root lecture-06 files | 40 PDFs, 1,461 pages and 39 ODPs inspected; 34 instructional PDFs, 1,261 pages after announcement/`xlect` exclusion | Primary source for the current revised first unit and sex-linked exercises |
| `OLD-*`, `PREVIEW`, templates, media and aggregate text files | Inventoried as alternate/supporting material | Their presence does not independently establish current scope |

The three 2025 PDF-only files are the crossover sheet, `lect05h-epistasis 2`, and the deletion guide.
Alternate exports and repeated examples do not count as additional concepts. Both 2026 probability
concept decks are present; the `v2` deck provides the revised sequence used below. Its notes mark
pp40-42 as study references to skip during live teaching, so those pages are not used to justify
a new live-lecture topic. Neither year's reviewed ODPs declares hidden slides. Presenter notes are
corroboration, not a separate student-facing assessment target.

The instructor's retirements override residual slides: classical experiments/discoveries, genetic
code concepts, PCR amplification calculations, DNA melting/helix structure, and Southern probes
remain outside genetics expansion. Inbreeding calculations remain time-deferred. Extensive 2025
matrix/tree activities do not override the deliberate move toward other tree assessments.

## Current skills and coverage

Locators are **PDF pages**, starting at one. `26U1` means `Current-Unit_1-2026/`, `26R` means the
2026 lecture-folder root, and `25U2` means `Current-Unit_2-2025/`. BPQ prefixes `I/`, `D/`, and `YM/`
use the source definitions in [GENETICS_EXAM_BPQ_AUDIT.md](GENETICS_EXAM_BPQ_AUDIT.md).

| Skill and visible lecture evidence | Actual BPQ relationship | Decision |
| --- | --- | --- |
| Use family evidence to infer individuals' possible genotypes and carriers. `26U1/lect05c-pedigree.pdf`, pp24-50 | Configured pedigree writers identify/select/match inheritance modes. `pedigree_lib/cli.py:102-116` does not grade an individual's carrier posterior. Mixed-disease stories can require some obligate-carrier reasoning as an intermediate | Extend individual-level pedigree questions; keep certainty, possible genotype, and posterior probability distinct |
| Restrict the sample to dominant-phenotype offspring, giving `P(Rr given round)=2/3`. `26U1/lect05d-v2-probability_concepts.pdf`, pp27-29; `lect05e-probability_problems.pdf`, pp17-23 | Configured lethal-survival questions condition on survival but ask phenotype ratios/counts. No direct configured heterozygote/carrier posterior item was found | High priority, including a simple phenotype-conditioned genotype task before a complex pedigree |
| Unequal pollen success changes gamete frequencies; multiply weighted cells and add genotype routes. `26U1/lect05d-v2-probability_concepts.pdf`, pp5,13-24; `lect05g-more_probability_problems.pdf`, pp2,6-11 | No matching unequal-gamete/pollen writer found in targeted BPQ searches. Ordinary dominance probability and unique-count sources assume different tasks | Add a weighted-gamete question with the frequencies stated or derived from supplied success weights |
| Select only round F2 offspring, then predict their testcross descendants. `26U1/lect05g-more_probability_problems.pdf`, pp12-15; objectives p2 | Unlisted `I/two_gene_selected_offspring_bonus.py:22-28,105-157` already computes selected-phenotype genotype weights, crosses the selected offspring, and tests failure to condition | Reuse/review an existing family for course inclusion before creating another generator; simple one-locus conditioning remains a distinct small target |
| X-linked parent inference and joint AD + XLR outcomes. `26R/lect06d-x_linked_genes_1.pdf`, pp28-30,47,51-54 | Configured reciprocal-cross, `poisson_flies.py`, and mixed AD + XLR sources already ask these forms of reasoning | Preserve existing coverage; current slides do not establish an AR + XLR multigeneration requirement |
| ZW inheritance with a Z-linked recessive lethal; distinguish conceived versus surviving offspring. `26R/lect06d-x_linked_genes_1.pdf`, pp22-23,55-61; p60 square shows the lethal female | ZW vocabulary, X-linked heterozygote tasks and autosomal lethality are adjacent coverage; no equivalent configured Z-linked cross was found | High priority. Start with the taught lethal/survival model; codominant bird variants are secondary exam-led possibilities |
| Incomplete dominance and standard epistatic F2/testcross/pathway reasoning. `26U1/lect05f-degrees_of_dominance.pdf`, pp10,29-31; `lect05h-epistasis.pdf`, pp47-50,70-76 | Dominance classification and standard epistasis are configured. Unlisted `I/two_gene_dominance_probability.py:205-217` asks numerical probabilities for independently expressed traits | Preserve these families; a numerical dominance variant can reuse existing work. Do not elevate combined incomplete-dominance/epistasis from historical exams alone |
| Parent-genotype inference from evidence. `26U1/lect05b-unknown_genotype_problems.pdf`, pp11-17 | Configured `D/who_father_html.py` infers paternity from gel inheritance; `I/monohybrid_litter_inference.py:136-178` infers a parent genotype from offspring phenotype counts | Existing reverse inference is substantial. A locus-specific gel-to-genotype question is a context/representation variant, not a wholly absent inference family |
| Drosophila X:autosome constitution and sex/viability. `26R/lect06e-x_linked_genes_2.pdf`, pp12-17 | Sex-system YAML defines systems; human aneuploidy writers interpret karyotypes. Neither establishes this species-specific X:A task | Current conceptual candidate below carrier/Z-linked/weighted-probability work; specify autosomal complement |
| Explicit PD/NPD/TT classification before map calculation. `25U2/lect09c-tetrads_2_activity_format.pdf`, pp5-19,27-43 | Configured tetrad writers grade distance/linkage/order and describe classification as an intermediate | A small graded classification mode is supported; no new mapping engine is needed |
| Reciprocal-translocation product balance/viability. `25U2/lect13d-meiosis_translocation.pdf`, pp31-50 | Existing gamete/product and segregation-label tasks cover much of this; explanatory viability/probability steps remain partial | Secondary extension using the existing representation and explicit model assumptions |
| Robertsonian fusion. The same 2025 deck, pp51-56 | Existing Robertsonian generator already asks for alternate-segregation gametes; a dosage-after-fertilization item would go beyond the visible lecture exercise | Retain technical gap in exam ledger; defer expansion until this calculation is part of current instruction |
| Triploid gamete probability and trisomic transmission. `25U2/lect11b-polyploidy.pdf`, pp44-45; `lect10d-chromo_aneuploid.pdf`, pp44-50 | Configured `I/polyploid/polyploid-gametes.py` chooses even ploidies and asks chromosome count. Cytogenetic notation does not assess trisomic segregation | Distinct later-unit possibilities; require current-course relevance before ranking them above confirmed 2026 exercises |
| Genome versus exome versus selected SNP genotyping. `26U1/lect03f-whole_genome_analysis.pdf`, pp18-23 | T1 terminology covers gene/genome/genomics; unlisted `YM/biotechnology/dna_sequencing.yml` describes sequencing technologies, not which genomic regions an assay samples | A secondary conceptual comparison candidate. Use supplied regions/coverage, rather than memorizing slide prices or product specifications |

## Course areas already represented

The exam audit establishes substantial configured coverage of disorders/terminology; Chargaff and
complementarity; restriction cuts/maps; blood/HLA typing and fingerprinting; Mendelian cross/count
reasoning; ABO/dominance/epistasis; sex-linked inheritance; chi-square; linkage/deletion mapping;
cytogenetic notation and chromosome counts; allele frequencies and Hardy-Weinberg concepts; and
tree topology comparisons. The lecture survey reinforces that structure. It does not justify adding
a duplicate generator for each slide or recreating every historical short-answer format.

For later units, 2025 visible instruction also includes auto/allopolyploid origin
(`lect11b-polyploidy.pdf`, pp28-34), X inactivation/Barr bodies (`lect11c-sex_dosage.pdf`, p11 onward),
and matrix/UPGMA activities (`lect12b-gene_trees.pdf`, pp39-64; `lect12c-more_gene_trees.pdf`, pp5-39).
The first two are secondary source-check candidates; expanded matrix assessment remains deferred
by the instructor's decision. No maintained 2026 second-unit successor is present in the supplied
2026 folder at this snapshot.

## Evidence and limits

Every selected PDF has an extracted text file. Paired ODP XML was inspected for slide visibility,
presenter notes and export differences. Decisive diagrams were visually reviewed, including the
Z-linked lethal Punnett square, phenotype-conditioned probability, tetrad activities, and chromosome
examples. PDF text omits some diagram labels, highlighted cells and image-only exercises; absence
from text alone is not treated as absence from the lecture. No source slides or exam originals were
changed. Local source manifests retain file hashes and counts under
`output_genetics_audit/lectures_2025/` and `output_genetics_audit/lectures_2026/`.

BPQ coverage is based on student-facing prompts, answer construction, configured task rows and
nearby unlisted sources. An internal posterior calculation counts as relevant infrastructure only
when a question uses it; the selected-offspring source does, inheritance-mode diagnostics alone do
not. No BPQ generators, website build, LMS import or runtime acceptance lane was run for this
documentation survey. Expansion candidates remain reviewable future work, not changes to the task
lists or an instruction to restore retired topics.
