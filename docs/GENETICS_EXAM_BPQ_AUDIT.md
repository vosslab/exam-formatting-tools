# Genetics exam and BPQ audit

Date: 2026-10-13. Purpose: distinguish useful BPQ expansion from historical exam content that
has intentionally left the course. This is a source-content audit, not a generator release test.

## Findings and course scope

The genetics task lists cover the main current course areas. The most useful remaining work is
**deeper reasoning within existing areas**, especially pedigree carrier inference, Z-linked bird
crosses, combined inheritance probabilities, and chromosome dosage after fertilization.
Existing implementations already cover several apparent gaps in the earlier inventory-only audit.

The instructor clarified the following during this audit. These decisions override priorities
in the earlier [GENETICS_EXAM_BPQ_AUDIT.md](archive/GENETICS_EXAM_BPQ_AUDIT.md):

| Historical material | Current instructional decision | Audit consequence |
| --- | --- | --- |
| Classical genetics experiments and discoveries | No longer covered in lecture | Historical coverage only; no genetics expansion recommendation |
| Genetic code concepts | No longer covered in lecture | Historical coverage only |
| PCR amplification calculations | No longer covered in lecture | Intentional omission, not a genetics-bank deficiency |
| DNA melting temperature and helix structure | No longer covered in lecture | Retire the old Tm/groove/form recommendations; retain current base-pairing/nucleotide tasks |
| Southern blot probe interpretation | No longer covered in lecture | Intentional omission |
| Pedigree inbreeding calculations | Often not reached because of course time | Defer; distinguish these from carrier-probability questions still present in 2025 |
| Distance-matrix interpretation for trees | Scaled back; better tree assessments now available | Preserve existing options; prioritize topology/relationship questions, not expanded reconstruction |

Primer design, transcription, and older laboratory-method questions are recorded below, but their
historical presence alone does not establish a current teaching need. No course task lists or BPQ
implementations were changed. Recommendations are candidates, not a newly approved syllabus.

## Evidence and interpretation

Reviewed all nine exam PDFs (131 pages), the six corresponding native DOCX/ODT files, the archive
source manifest, both current genetics task CSVs, and the student-facing question construction in
relevant BPQ Python/YAML sources. Read every PDF's extracted text and inspected 24 selected rendered
pages covering helices, probe maps, gels, mitosis, pedigrees, tables, translocations, and trees.
Native formats corroborate question text and expose extraction differences; they are not counted
as additional exams. The 2019 and 2025 PDFs have later export dates, so filenames identify the exam
family, not a verified date of classroom administration.

The prior audit omitted the 2017 final and did not have local BPQ source access. It is retained as
historical evidence. This document supersedes its coverage judgments and proposed expansion order.

Use [GENETICS_EXAMS_INDEX.md](../ARTIFACTS/GENETICS_EXAMS_INDEX.md) to open the searchable,
image-free Markdown companions and original PDFs. The companions preserve question wording,
choices, text tables, and numbering; they are intentionally lossy and are not answer keys.

Coverage terms:

- **Covered:** configured source asks for substantially the same reasoning, even with different
  names, numbers, organisms, or answer format. This does not certify runtime/rendering quality.
- **Partial:** relevant source exists, but an assessed step, conditioning assumption, or constructed
  response is missing from its student-facing task.
- **Elsewhere:** relevant BPQ source exists but is absent from these two genetics task lists.
- **Not found:** no matching student-facing implementation found in the inspected sources and
  targeted repository searches. This is bounded evidence, not proof about every historical branch.
- **Historical/deferred:** a curriculum decision, independent of technical coverage.

A repeated question across years counts as one skill. Conversely, recognizing a pedigree pattern,
inferring an obligate carrier, and calculating an inbreeding coefficient are three skills. Internal
solver functions do not count as coverage unless a student-facing question actually asks for them.
Blank working tables do not establish that table completion is graded.

### Source locations and snapshot

The local checkout contents on the audit date are authoritative. The identifiers below are local
source locators, not claims about what is published on the website or committed upstream.

- BP root: `/Users/vosslab/nsh/PROBLEMS/biology-problems/problems`.
- Website root: `/Users/vosslab/nsh/PROBLEMS/biology-problems-website`.
- T1: `task_files/genetics_tasks1.csv`, 81 nonblank genetics rows, seven topics.
- T2: `task_files/genetics_tasks2.csv`, 49 nonblank genetics rows, four topics.
- Together: 130 configured rows referencing 89 distinct Python/YAML assets. Difficulty levels,
  modes, and repeated pedigree entries are not 130 different concepts.
- Source prefixes in tables: `I/` = `inheritance-problems/`; `M/` =
  `molecular_biology-problems/`; `D/` = `dna_profiling-problems/`; `YM/` =
  `matching_sets/`; `YS/` = `multiple_choice_statements/`, all relative to BP root.
- T1 SHA-256: `6cb99f135cfcde057867ccd9e85275587750b445ee72e85cdcb06ec18b106426`.
- T2 SHA-256: `d6a1053eeb31fa2c24f8627272d8faba58fb32c8446d32deb05e695d6a7329d9`.

The [genetics_exam_sources.tsv](../ARTIFACTS/genetics_exam_sources.tsv) has 79 source rows;
11 rows map to the six older representative PDFs added in the archive cleanup. Their MD5 values
match the actual artifacts. The manifest is not a complete provenance record for the pre-existing
2019 final and 2025 native/PDF sets. Set-aside files and the incomplete 2018 midterm are outside
this audit. The manifest's set-aside directory is not present in this checkout.

## Current-course coverage matrix

References use M = midterm, F = final, Q = numbered selected-response item, SA = short answer.
Numbers restart in SA and Fun Points. Page references below are PDF page numbers, starting at one.

### Foundations and DNA analysis

| ID | Exam skill and evidence | Actual BPQ evidence | Judgment |
| --- | --- | --- | --- |
| C01 | Disorder descriptions: 2025 M Q1-4; F Q1-6 | T1 `YM/inheritance/genetic_disorders.yml`; T2 `I/cytogenetic_notation/cytogenetic_notation-disorders.py` includes syndrome/description/notation prompts | Covered at concept level; exact matching layouts need not be duplicated |
| C02 | Gene/genome/genetics/genomics: 2016 M Q86-90; 2025 M Q5-8 | T1 `YM/inheritance/genetics_terminology.yml` explicitly includes all four; `mendelian_genetics_terms.yml` includes genotype/phenotype/allele | Covered; remove the prior terminology-gap suggestion |
| C03 | Nutrient rescue given an ordered pathway and a blocked enzyme: 2025 M Q9; F Q7 | T1 `M/beadle_tatum-metabolic_pathway.py`, `write_question`, lines 43-85, asks which supplements restore growth and emits MA | Covered, including multiple-correct answers |
| C04 | Infer pathway order, wild type, first/last substrate, or blocked step from a growth matrix: 2017 M Q6-9; 2017-2019 F Q1-4; 2019 M Q2-5 | `M/mutant_screen.py`, lines 79-110, asks for full pathway order (FIB) or wild-type class (MC); not in T1/T2. C03 gives the pathway rather than inferring it | Elsewhere for order/wild type; first/last-step prompts remain partial. Optional historical enrichment, not scientist-history restoration |
| C05 | Chargaff percentages and directional complementarity: 2016 M Q1,4,11; 2025 M Q10,12; F Q8,10 | T1 `M/chargaff_dna_percent.py` asks other-three-base percentages; `complementary_sequences.py` supports directional and directionless MC/FIB | Covered |
| C06 | Nucleotide components, RNA/DNA distinctions and basic DNA chemistry: 2016 M Q2,8; 2017 M Q15-17; 2025 M Q11,13 | T1 `YS/biochemistry/nucleotide_components.yml`, `rna_v_dna.yml`, `dna_structure-biol_351.yml` | Covered. Do not infer a need to restore retired groove/Tm instruction from these retained fundamentals |
| C07 | Palindrome identification/completion; cut type and overhang sequence: 2016 M Q19-24; 2025 M Q14-20; F Q11-16 | T1 `YS/english_palindromes.yml`; `M/palindrome_sequence_match.py`; `M/restriction_enzymes/overhang_type.py`, `overhang_sequence.py` | Covered; matching, MC, and some FIB modes already exist |
| C08 | Linear fragment vs long-strand digestion, circular maps, visible band sizes: 2016 M Q26-33; 2017 M Q25-29; 2025 F Q17-20 | T1 `M/restriction_enzymes/linear_digest.py` has fragment/strand modes and MA band-size answers; `circular_digest.py` also emits MA | Covered for single-enzyme digestion and endpoint distinction. Older combined-enzyme digests are partial: current prompts explicitly digest with one enzyme only |
| C09 | Paternity and crime-scene gel comparison: 2016 M Q17-18; 2017-2019 exams; 2025 M Q23-24, F Q21-22 | T1 `D/who_father_html.py`, `who_killer_html.py` construct gel evidence and ask for the matching individual | Covered. Do not invent an inconclusive-result requirement from questions that only ask for an identification |
| C10 | Agglutination including Rh and invalid control: 2019 M Q32-35; 2025 M Q25-28; F Q23 | T1 `D/blood_type_agglutination_test.py` asks which test pattern fits a blood type, with control patterns in choices | Covered for valid type-to-pattern recognition; explicit invalid-test identification is a small additional target, not a missing blood-typing family |
| C11 | HLA haplotype inheritance: 2016 M Q25, SA2; 2018 F SA2; 2025 F Q24-25 | T1 `D/hla_genotype.py`, two- and three-locus rows, selects a possible offspring genotype | Covered for transmission; partial for listing all four parental haplotype combinations |

### Crosses and family inference

| ID | Exam skill and evidence | Actual BPQ evidence | Judgment |
| --- | --- | --- | --- |
| C12 | Mendelian vocabulary, principles, parental/test crosses and F1/F2 outcomes: 2017 M Q36-47; 2025 M Q30-46; F Q26-39 | T1 Mendel matching YAMLs; `I/monohybrid_genotype_statements.py`, `punnett_choice.py`, `monohybrid_litter_inference.py` | Covered for cross identification and genotype inference. Explaining limits/counterexamples to all four principles (2017 F SA1) is a broader written reasoning task |
| C13 | Count distinct gametes, offspring genotypes and phenotypes: 2016 M Q43-51; 2025 M Q36-39; F Q30-33 | T1 `I/large_crosses/unique_gametes.py`, `unique_cross_genotypes.py`, `unique_cross_phenotypes.py` delegate to `unique_counts_lib.py`; lines 137-173 ask for counts | Covered. Current helper supports shared scenarios and working tables; these do not grade complete gamete lists or every Punnett cell |
| C14 | Multiply probabilities for a particular multilocus genotype/phenotype: 2016 M Q52-53; F Q23-24; 2017 M Q67; 2019 M Q77 | C13 counts possibilities; `I/probabiliy_of_progeny.py` is binomial sex-count probability, not an arbitrary multilocus outcome calculator. `I/two_gene_dominance_probability.py` exists outside lists for two independently expressed traits | Partial. Specific-genotype probability and number of unique genotypes are different targets; do not create another counting generator |
| C15 | Dominance classification from phenotype/Punnett display: 2017 M Q52-54; 2025 M Q54,56-57,65; F Q49-53 | T1 `YM/inheritance/degrees_of_dominance.yml`, `I/monohybrid_degrees_of_dominance.py` asks which dominance model explains the displayed results | Covered for classification; partial for numerical offspring probabilities under codominance/incomplete dominance |
| C16 | ABO possible offspring/parent types and family constraints: 2016 M Q42; 2017 M Q62-63,73; 2025 M Q62-63; F Q54-55 | T1 `I/blood_type_offspring.py` returns possible child phenotypes; `blood_type_mother.py` infers possible mother types from father/child | Covered for possibility sets; partial for exact probabilities after inferring genotypes from several relatives or for reverse father-specific wording |
| C17 | Lethality and conditioning on survival: 2016 M Q55; 2025 M Q64 | T1 `I/lethal_allele_survival.py` explicitly distinguishes all offspring, surviving offspring, expected counts, and phenotype ratios | Covered for one autosomal lethal locus. The old two-locus surviving subset is a meaningful extension, not a missing lethal-allele topic |
| C18 | Standard epistasis ratios, metabolic explanations, F2/testcross conversion: 2016 M Q57-58; 2017 M SA3; 2019 M SA4; 2025 M Q47-53; F Q40-46 | T1 `I/epistasis/dihybrid_cross_epistatic_gene_interactions.py`, `dihybrid_cross_epistatic_gene_metabolics.py`, `epistasis_test_cross.py --forward/--inverse` | Covered for identifying interactions and ratios. `hybridcrosslib.py` includes 10:3:3 and 12:4 as well as standard ratios; unusual wording alone is not a gap |
| C19 | Combine epistasis with incomplete dominance and derive a new ratio: 2025 M SA3, p12 | C18 models complete-dominance phenotype partitions; ratios in `I/hybridcrosslib.py:70-83` omit this model. Unlisted `two_gene_dominance_probability.py` treats independently expressed traits without masking | Partial; real missing interaction, even though both component concepts exist |
| C20 | Identify inheritance from pedigrees or choose a matching pedigree: 2017 M Q60; 2017 F Q50-53; 2019 M Q67-70; 2025 M Q58-61 | T1 `I/pedigrees/write_pedigree_to_pattern.py`, `write_pattern_to_pedigree.py`, `write_pedigree_pattern_matching.py` provide identify/select/matching tasks | Covered. Both autosomal-only and full inheritance-pattern rows are configured |
| C21 | Infer named individuals' genotypes, obligate carriers and conditional carrier probabilities; draw a pedigree from prose: 2016 M SA1; 2017 M Q61, SA1; 2017-2019 F pedigree SA; 2019 M SA1; 2025 M SA2 and F SA1 | C20 asks for inheritance mode. `pedigree_lib` contains compatibility/genotype machinery, but its configured student tasks do not ask for these individual-level results | Partial/high priority. Probability diagnostics under `pedigree_lib/offspring_probability.py` evaluate fixed crosses; they are not a student carrier-inference generator |
| C22 | X-linked reciprocal crosses and reverse inference from sex-by-phenotype counts: 2016 M Q64-65; 2017 F Q54-55; 2019 F Q67-68; 2025 M Q81; F Q70 | T1 `I/x_linked_reciprocal_cross.py` predicts F1; `poisson_flies.py:125-178` presents counts and asks parental genotypes | Covered for forward F1 and reverse parent inference. `poisson_flies.py` is not merely a probability-distribution topic; an F2/grandchild follow-up is a further step |
| C23 | Autosomal-dominant plus X-linked-recessive joint probabilities: 2016 M Q66-75; F Q32-38; 2017 M Q80-84; 2019 M Q87-89 | T1 `I/dominant_and_X-linked_recessive.py` and `_variations.py` construct family stories and sex-conditioned joint events | Covered for their AD + XLR model. Do not generalize that coverage to every pair of inheritance models |
| C24 | Autosomal-recessive plus XLR carrier/affected union, then transmission to a grandson: 2025 M Q82-84, p8 | C23 is specifically autosomal dominant plus XLR and asks phenotype events. C21 is pattern classification; neither supplies this AR + XLR, carrier-or-affected, multigeneration task | Partial/high priority; retain the reasoning but review and replace the questionable disease story |
| C25 | Z-linked codominance and lethal-allele crosses: 2016 M SA8; 2019 F extra SA2; 2025 M Q66, SA1; F Q56 | T1 `YM/inheritance/sex_determination.yml` defines ZW; `x_linked_tortoiseshell.py` handles an X-linked heterozygote phenotype; C17 handles autosomal lethality | Not found as Z-linked student crosses; adjacent implementations are not equivalent. Current 2025 evidence makes this a stronger expansion candidate than retired molecular topics |
| C26 | Inversion-associated mating rules and joint sex/stripe probabilities: 2017 F Q88-89; 2018-2019 F Q87-88; 2025 F Q62-63 | C12/C14 supply independent segregation reasoning but no sparrow-style constrained mating scenario; rearrangement YAML defines inversion | Partial/contextual extension. Simple 1/2 and 1/4 predictions may reuse cross logic; the 2019 draft's absent-gene model is a separate, unfinished case |
| C27 | Exactly k boys/girls among n offspring: 2016 F Q47; 2017 M Q92; 2018 F Q41; 2019 M Q91 | T1 `I/probabiliy_of_progeny.py:330-383` explicitly asks this binomial problem | Covered; spelling of the source filename is intentional in this locator |

### Chromosomes, mapping and trees

| ID | Exam skill and evidence | Actual BPQ evidence | Judgment |
| --- | --- | --- | --- |
| C28 | Meiosis vocabulary, prophase-I events, mitosis/meiosis distinctions and sex systems: 2016 M Q60-61,91-95; 2017 F Q40-48; 2025 M Q72-80; F Q47,57-61 | T1 `YM/inheritance/meiosis_terms.yml`, `meiosis_prophase_1.yml`, `sex_determination.yml`; `YS/cell_biology/mitosis_and_meiosis.yml` | Covered for listed terminology and general division products. S-phase timing, karyotype-stage selection, multinucleation and stage-specific chromosome/chromatid counts are not all established by those banks |
| C29 | Recognize mitotic stages in microscopy: 2017 M Q68-71; 2019 M Q78-81 | C28 is text-statement/definition content; no corresponding configured micrograph-identification task | Partial, historical format-specific opportunity; lower priority than current cross reasoning |
| C30 | Chi-square null/alternative, expected counts, statistic, errors and decision: 2016 F Q40-46; 2017 M Q93-100; 2019 M Q94-100; 2025 M Q92-100; F Q64-69 | T1 `I/chi_square/chi_square_calculated.py`, `chi_square_choices.py`, `chi_square_errors.py`, `chi_square_hypotheses.py`, `chi_square_hypotheses_lab_partner.py`, plus statistical YAML | Covered for the main test workflow. Exact cell-by-cell grading, df/critical-value selection and bracketing a p-value from a table are partial as standalone targets; do not call the whole chi-square family missing |
| C31 | Two-/three-point linkage, cis/trans, parental/recombinant classes, distances/order and interference: 2016 F Q50-62; 2017 F Q56-68; 2018-2019 F Q56-66; 2025 F Q71-79 | T2 `I/gene_mapping/two-point_test_cross-*` and `three-point_test_cross-*`; `three-point_test_cross-which_genotypes.py --genes` explicitly grades all recombinants; `*distances_plus.py` grades distances/order; `*find_interence.py` grades interference | Covered for computational/identification skills, including MA. Explaining the 50% recombination ceiling is a small conceptual extension; it is not another mapping engine |
| C32 | Classify each unordered tetrad as PD/NPD/TT, identify parental phase and calculate distance: 2016 F Q63-69; 2017 F Q69-75; 2018 F Q69-75; 2019 F Q69-74/XXX; 2025 F Q80-86 | T2 unordered two-/three-gene scripts ask distance, linkage, or distances plus order. `tetrad_unordered_three_gene-distances_plus.py:93-107` instructs students to assign PD/NPD/TT as an intermediate step | Covered for mapping; partial for explicitly graded per-tetrad classification and parental-phase selection. A small diagnostic question mode is sufficient |
| C33 | Deletion-overlap gene ordering, including a word answer: 2016 F Q70; 2017 F Q76; 2018 F Q76, SA1; 2019 F Q75-76, SA1; 2025 F SA2 | T2 `I/deletion_mutants/deletion_mutant_random.py`, `deletion_mutant_words.py`, with MC/FIB capability | Covered; current code already supports constructed sequence answers |
| C34 | Cytogenetic notation, named aneuploidies, chromosome arms/bands: 2017 F Q84-86; 2018-2019 F Q84-85; 2025 F Q1-6,88 | T2 all five `I/cytogenetic_notation/cytogenetic_notation-*.py` sources | Covered for syndrome/notation interpretation. The molecular cause of light/dark G bands is a separate older concept |
| C35 | Rearrangement names, chromosome shapes and pericentric-inversion effects: 2016 F Q78,81; 2017-2019 F Q78-83 | T2 `YM/inheritance/chromosome_alterations.yml`, `chromosome_shapes.yml`; C34 rearrangement interpretation | Covered for terminology; partial for deriving a changed centromere position/shape from a specified rearrangement, and auto- vs allopolyploid origin |
| C36 | Reciprocal translocation products and adjacent-1/adjacent-2/alternate gametes: 2016 F Q71-77; 2019 F Q89, SA2; 2025 F Q89,92-97 | T2 `I/translocation/letter_translocation_problem_color.py`; `translocation_meiosis_table.py:12-134` asks students to select two gametes for a named segregation type | Covered for products/classification (exam and generator reverse the direction of the matching). Partial for constructing all gametes, assigning probabilities and explaining viability |
| C37 | Robertsonian gamete leading to trisomy after fertilization: 2025 F Q98, p13 | T2 `I/translocation/robertsonian.py:10-16` asks which gamete arose by alternate segregation, not which produces Down syndrome after fertilization | Partial/high-value extension: carry chromosome-arm dosage through fertilization rather than classify segregation alone |
| C38 | Monoploid/haploid/gamete chromosome counts: 2016 F Q82; 2017-2019 F Q77; 2025 F Q90-91 | T2 `I/polyploid/polyploid-monoploid_v_haploid.py`, `polyploid-gametes.py` explicitly ask both | Covered |
| C39 | X dosage compensation, Barr bodies, species-specific sex determination/fertility: 2016 F Q79-80; 2017 F Q87; 2018-2019 F Q86; 2019 M SA2; 2025 F Q87 | T1 sex-system YAML and tortoiseshell crosses are related; T2 aneuploidy scripts identify human karyotypes. No matching Barr-body or Drosophila X:autosome-ratio problem found | Partial; optional conceptual extension if still taught. Avoid treating XY vs ZW terminology as coverage of dosage mechanisms |
| C40 | Allele/genotype frequencies and consequences of nonrandom mating: 2016 F Q91-93; 2017-2018 F Q90,92-93; 2019 F Q90-92,100 | T2 `I/hardy_weinberg/hardy_weinberg_numeric.py` computes allele frequency from genotype/phenotype data; `hardy_weinberg_mc_type.py` identifies p/q/p^2/2pq/q^2; population-genetics YAML explicitly includes consanguinity and increased homozygosity | Covered for genotype-count allele frequency, variable identification and qualitative inbreeding effects. The configured numeric default is `--1a`; disease-incidence/dominant-phenotype variants `--2a/--2b` exist but are not selected by the current row. Partial for direct numerical carrier/homozygote frequency outputs where numeric templates ask for p or q |
| C41 | Topology equivalence/difference and closest relationships: 2016 F Q83; 2017-2018 F Q91; 2025 F Q99 | T2 `I/phylogenetic_trees/gene_tree_matches_plus.py --same/--different` directly asks topology equivalence | Covered; aligns with the instructor's preferred direction for tree assessment |
| C42 | Distance matrix to tree, closest pair, branch length, matrix completion and drawn reconstruction: 2016 F Q84-86; 2017 F Q94-96, SA3; 2018 F Q94-96, SA4; 2019 F Q93-95, SA4; 2025 F Q100 | T2 `I/phylogenetic_trees/gene_tree_choice_plus.py:455-518` actually presents a distance matrix and asks students to select a tree | Covered for matrix-to-tree selection; partial for intermediate arithmetic and free drawing. Deliberately scaled back; no expansion priority |
| C43 | Relatedness, common ancestors, valid loops and pedigree inbreeding coefficient: 2016 F Q87-90; 2017-2018 F Q97-100 and pedigree SA; 2019 F Q96-99, SA5f | C20 labels inheritance; C40 discusses consanguinity and its effects. An internal F adjustment in Hardy-Weinberg numeric data generation is not a student pedigree-coefficient task | Not found as a configured student calculation. Defer because lecture time is limited; do not merge this with C21 carrier inference |

## Historical coverage register

These observations preserve the complete survey without turning retired lecture content into a
backlog. An existing generator elsewhere is a reuse lead only if that material returns to teaching.

| Historical skill | Exam evidence | BPQ source evidence and limitation |
| --- | --- | --- |
| Scientist/discovery matching and classical experiment outcomes | 2016 M Q76-85; 2017 M Q11-14; 2017 F Q5-6; 2018-2019 F Q5; 2019 M Q6-9 | No matching scientist/experiment bank found. Beadle-Tatum rescue and mutant-screen generators assess pathways, not historical attribution. Intentionally retired |
| Redundancy, codon capacity, gene-product concepts | 2016 M SA3, SA5; 2017 M Q4; 2017 F Q7; 2018-2019 F Q6; 2019 M Q1 | T1 genetics terminology defines genetic code but does not test redundancy or codon-capacity arguments. Unlisted `M/translate_genetic_code.py` and `YM/molecular_biology/central_dogma_terms.yml` are adjacent, not substitutes for every historical concept. Intentionally retired |
| PCR target fraction after ideal amplification | 2016 M Q9; 2017 M Q20, F Q12; 2018-2019 F Q13; 2019 M Q17 | Not found as the same target-length/background/cycle calculation. `M/RT-qPCR.py` is Ct-based expression analysis, a different problem. Intentionally retired |
| Primer design and PCR principles | 2016 M Q7, SA7; 2017 M SA2; 2019 M SA3 | Unlisted `M/pcr_design.py` selects a pair of oriented primers; `inverse_pcr_design.py`, `nested_pcr_design.py` and `YS/molecular_biology/pcr_*.yml` also exist. Primer design is therefore not a wholly missing BPQ family. No priority inferred from its presence in old exams |
| DNA Tm vs base composition | 2016 M Q6, F Q4; 2017 M Q18, F Q8; 2018-2019 F Q7; 2019 M Q19 | Unlisted `M/dna_melting_temp.py` and `YS/biochemistry/melting_Tm_type_1.yml`, `_type_2a.yml`, `_type_2b.yml` cover Tm reasoning. Intentional omission from genetics |
| Major/minor groove diagrams and A/B/Z helix forms | 2016 M Q13, F Q7; 2017 M Q19, F Q9; 2018 F Q10; 2019 M Q18 | Current DNA/RNA YAML mentions grooves but does not ask diagram localization. No matching configured visual task found. Intentionally retired |
| Southern blot probe selection of digest fragments | 2017 M Q30-31, F Q10-11; 2018-2019 F Q11-12; 2019 M Q29-30 | Digest sources compute bands without a hybridization-probe filter; no equivalent probe task found. Intentionally retired |
| Template transcription and synthesis direction | 2016 M Q3,5,12; F Q6; 2017 M Q10; 2019 M Q14 | Unlisted `M/rna_transcribe.py`/`rna_transcribe_lib.py` implement template transcription with direction modes; central-dogma YAML supplies process terminology. An inclusion question, not grounds for a duplicate generator |
| Gel migration mechanisms and method vocabulary | 2016 M Q14-16, SA4; F Q8 | Profiling/digest questions use gels without asking electric-charge/migration explanations. Unlisted `YM/laboratory/protein_v_dna_gels.yml` distinguishes technique components, but does not fully cover those mechanism questions. Low-priority historical content |
| Course-specific graduate presentations | 2016 F Q94-100 | Cardiomyopathy protein, cilantro perception, pollinator traits, pandoravirus, two disease-inheritance talks, Neanderthal comparison. Some disease concepts overlap existing banks; the presentation-specific recall is not a reusable genetics-bank requirement |
| Course feedback and Fun Points | 2016 M SA9; bonus sections in all other exams except 2016 F | Recorded in companions; excluded from genetics expansion. Includes films, riddles, parking/triangle puzzles, combinatorics, and relativity |

## Expansion priorities

Priorities follow the instructor's scope clarification, recurrence, and distinct reasoning value.
An additional unlisted reuse lead is `I/two_gene_selected_offspring_bonus.py`: it conditions on a
selected plant offspring's phenotype before predicting a second cross. That is useful probability
infrastructure, but it does not supply pedigree carrier inference or the AR + XLR family task.
A question family can be reused in several formats; adding formats alone is not a content priority.

| Rank | Candidate | Smallest useful student task | Existing owner to extend | Completion evidence for future implementation |
| --- | --- | --- | --- | --- |
| 1 | Individual-level pedigree inference (C21) | Identify obligate carriers, select possible genotypes for a named person, and calculate carrier probability conditional on being unaffected | Existing pedigree model/solver and question writers | One visible pedigree supports an independently checked answer; distinguish certainty, possibility and conditional probability; include a 2/3 unaffected-sibling case and an obligate-carrier case |
| 2 | Z-linked crosses (C25) | Predict sons/daughters for a ZZ x ZW cross with codominance; separately condition on survival for a Z-linked lethal | Inheritance cross/scenario layer, reusing display conventions from X-linked tasks | Enumerated gametes agree with each sex-specific outcome; denominator states all offspring vs one sex vs survivors; lethal expression in hemizygous females is explicit |
| 3 | Joint carrier and multigeneration probability (C24) | Combine AR carrier-or-affected status with XLR carrier status; follow transmission to a grandson | Mixed-inheritance probability source, sharing cross logic rather than copying stories | Independently enumerate both loci, carry the correct conditioning information forward, and avoid impossible or contradictory parental histories |
| 4 | Combined epistasis/incomplete dominance (C19) | Derive phenotype probabilities from a genotype-to-phenotype rule table; optionally derive F2 and testcross ratios | Existing epistasis/plant probability helpers | All 16 equally weighted F2 cells give the stated ratio. The 2025 model implies dark blue:light blue:white:pink = 3:6:3:4; testcross gives 0:1:1:2. Keep model rules explicit |
| 5 | Chromosome dosage after fertilization (C37, part of C36) | Given a gamete from a Robertsonian carrier and a normal partner, identify the resulting dosage/outcome | Existing translocation rendering and gamete representation | Trace each chromosome arm through fertilization. Distinguish balanced carrier, normal dosage, trisomy and monosomy; avoid inferring outcome solely from the segregation label |
| 6 | Small graded intermediate steps (C32, C30) | Label a tetrad PD/NPD/TT for a named gene pair; or select a p-value interval from a supplied chi-square table | Existing mapping/statistics scenario generators | Reuse the same input data across prompts with independent keys; do not expose a solved table that answers the new question |
| 7 | Focused probability variants (C14-C17) | Specific multilocus outcome, ABO probability after family inference, or dominance probability instead of classifying dominance | Existing cross/ABO sources; inspect unlisted `two_gene_dominance_probability.py` first | Demonstrate the reasoning missing from current tasks; avoid duplicating unique-count or standard monohybrid questions |

Ranks 1-5 are the strongest candidates from the 2025 exams. Rank 6 is useful for diagnosis/scaffolding,
not evidence that mapping or chi-square is generally absent. Rank 7 is smaller or more historical.
Double-enzyme digestion, full HLA enumeration, mitosis micrographs, dosage compensation, and
inversion-based contexts remain secondary candidates whose current lecture relevance should govern
selection. Inbreeding and expanded distance-matrix reconstruction stay deferred. Retired molecular
and history topics stay outside the proposed current-course expansion.

### Preserve constructed reasoning

The recurring short-answer tasks require drawing, listing all possibilities, explaining exclusions,
and showing calculations. Multiple-choice topic coverage does not automatically replace these
assessment demands. For example, C13's count is covered while a student's complete gamete list and
Punnett square are not graded by that count question. Existing FIB deletion-order and FIB+ mapping
sources show that constructed answers are already possible without inventing a new platform.

A useful first expansion is a small number of automatically checkable subquestions attached to one
scenario, with an optional instructor-marked explanation/drawing. Narrative-to-pedigree construction
is a distinct authoring/assessment feature and should not delay simpler carrier-inference prompts.

## Complete exam block inventory

This ledger accounts for the content of every representative exam, including short-answer and
non-course sections. Topic/skill IDs above carry the coverage decision. Repeated examples are not
separate proposed generators. Each exam heading links its searchable companion.

### 2016 midterm

[2016_GENETICS_MIDTERM.md](../ARTIFACTS/2016_GENETICS_MIDTERM.md), 13 PDF pages.

| Location | Content accounted for |
| --- | --- |
| p1-2, Q1-13 | Complementarity, RNA/transcription, Chargaff, elongation, Tm, PCR, DNA chemistry/form, phenotype; C05-C06 and historical register |
| p2-4, Q14-33 | Restriction/gel/Southern terminology, gels, palindromes, overhangs, HLA count, linear/circular single/double digests; C07-C11 and historical lab methods |
| p4-6, Q34-59 | Dominance/epistasis, sum/product rules, F2/parent inference, ABO, unique counts, multilocus probabilities, albinism carrier, lethal dihybrid, phenotype classes, Punnett size; C12-C19 |
| p6-7, Q60-75 | Meiosis/cell cycle, X-linked recognition/reciprocal cross, AD + XLR zygosity and sex-conditioned events; C22-C24,C28 |
| p8, Q76-95 | Ten scientists/discoveries; genetics vocabulary; prophase-I stages; historical register,C02,C28 |
| p9, SA1 | Narrative hemophilia pedigree, pattern justification, obligate carriers, Isabel carrier probability, Harriet's son's risk; C20-C21 |
| p10, SA2-4 | All HLA combinations; why codons need at least three bases; gel charge/size explanation; C11 and historical register |
| p11, SA5-7 | Gene-trait complexity; four-sample Chargaff table and possible identity; pentamer PCR primers; C05 and historical register |
| p12, SA8-9 | Z-linked lethal pigeon cross and sex-specific survival/carriers; course feedback; C25 and excluded feedback |
| p13, Fun 1-4 | Princesses, Jon Snow, nugget-count puzzle, triangles; excluded bonus |

### 2016 final

[2016_GENETICS_FINAL.md](../ARTIFACTS/2016_GENETICS_FINAL.md), 11 PDF pages.

| Location | Content accounted for |
| --- | --- |
| p1, Q1-11 | Complementarity/Chargaff/Tm/DNA structure/transcription/form; gel direction, palindrome/overhang; C05-C07 and historical register |
| p2-3, Q12-20 | HLA, two gels, linear/circular/long-strand digests; C08-C11 |
| p3-4, Q21-38 | F2 and parent inference, specific multilocus outcome, unique counts, ABO, mixed dominance, epistasis and AD + XLR; C12-C18,C23 |
| p5-6, Q39-49 | X-linked pattern, full sex-ratio chi-square, binomial children, X-linked F1 testcross; C20,C22,C27,C30 |
| p6-7, Q50-69 | Three-point mapping, recombinant sets, gene order/distances, expected/observed DCO and interference, tetrad categories/distance; C31-C32 |
| p8-9, Q70-82 | Deletion map, translocation segregation/products, inversion, Barr bodies, fly/human XXY, centromere shift, ploidy counts; C33-C39 |
| p9-10, Q83-93 | Elephant topology, distance-matrix tree, half-relative pedigree loop/coefficient, Hardy-Weinberg; C40-C43 |
| p10-11, Q94-100 | Seven graduate-presentation questions; historical register. No separate SA/Fun section |

### 2017 midterm

[2017_GENETICS_MIDTERM.md](../ARTIFACTS/2017_GENETICS_MIDTERM.md), 13 PDF pages.

| Location | Content accounted for |
| --- | --- |
| p1-3, Q1-24 | Disorder definition, DNA/code/Chargaff, mutant-screen matrix, transcription, four classical discoveries, nucleotide chemistry, Tm/groove, PCR fraction, palindromes; C01,C04-C07 and historical register |
| p3-4, Q25-34 | Circular digest, Southern probes, O+ agglutination, paternity/forensic gels; C08-C10 and historical Southern |
| p4-6, Q35-61 | Albinism, Mendel/testcross/F2 ratios, unique gametes, independence, disease-risk/carrier transmission, dominance, rare disorder patterns, pedigree mode/individual genotype; C12-C16,C20-C21 |
| p7-8, Q62-79 | ABO, 2^n gametes and offspring chromosome combinations, genotype probability, mitosis micrograph, homologs, unique counts, HLA; C11-C16,C28-C29 |
| p9-10, Q80-100 | AD + XLR, reciprocal cross, Y-lineage, daughter/grandson risks, pattern inference, multinucleation, binomial and full chi-square; C21-C24,C27-C30 |
| p11, SA1-2 | Cystic-fibrosis narrative pedigree/carrier reasoning; oriented PCR primers; C21 and historical primer design |
| p12, SA3 | Dihybrid Punnett completion, metabolic epistasis and F2/testcross ratios; C18, constructed reasoning |
| p13, Fun 1-4 | Princesses, Jon Snow, nugget counts, parking puzzle; excluded bonus |

### 2017 final

[2017_GENETICS_FINAL.md](../ARTIFACTS/2017_GENETICS_FINAL.md), 15 PDF pages.
This whole exam was absent from the prior audit's inventory.

| Location | Content accounted for |
| --- | --- |
| p1-2, Q1-17 | Mutant screen, classical experiments/gene product, Tm/groove/Southern/PCR, palindromes/cut; C04,C07 and historical register |
| p3-5, Q18-39 | Circular/long-strand digests, AB- typing, gels, Mendelian crosses/disorder patterns, dominance, multiallelic probability, unique gametes, epistasis; C08-C10,C12-C18 |
| p5-6, Q40-55 | Karyotype stage, crossover stage, independent births/binomial/life cycle/sex systems, XLR parent/F2 inference, pedigree matching; C20,C22,C27-C28 |
| p7-8, Q56-76 | Three-point mapping/interference, tetrad types/distance, deletion order; C31-C33 |
| p8-9, Q77-89 | Ploidy, chromosome shapes/allopolyploidy/banding, Turner/notation, fly dosage compensation, sparrow sex/stripe; C26,C34-C39 |
| p9-11, Q90-100 | Hardy-Weinberg/genotype and founder allele counts, elephant tree, distance matrix, relatedness/inbreeding loops; C40-C43 |
| p11-12, SA1-2 | Explain/counterexample Mendel's four principles; enumerate gametes/genotypes and construct a four-gene Punnett cross; C12-C14, constructed reasoning |
| p13-14, SA3-4 | Complete matrix/draw tree; narrative consanguineous pedigree, evidence, carrier risk, inbreeding coefficient; C21,C42-C43 |
| p15, Fun 1-4 | Star Wars, dwarves, eye riddle, relativity; excluded bonus |

### 2018 final

[2018_GENETICS_FINAL.md](../ARTIFACTS/2018_GENETICS_FINAL.md), 16 PDF pages.

| Location | Content accounted for |
| --- | --- |
| p1-2, Q1-18 | Mutant screen, classical experiment/gene product, Tm, complement, HLA, groove, Southern, PCR, palindromes/cut; C04-C07,C11 and historical register |
| p3-5, Q19-47 | Digests/typing/gels, inheritance patterns, Mendel/testcross/gametes/epistasis, cell-cycle/binomial/sex systems; C08-C10,C12-C18,C27-C28 |
| p6, Q48-55 | Joint ABO + XLR zygosity, sex-conditioned events and transfusion compatibility; C16,C23-C24 (partial for ABO combination/compatibility) |
| p7-8, Q56-76 | Three-point mapping/interference, XLR F2/reverse inference, tetrad classes/distance, deletion order; C22,C31-C33 |
| p9-10, Q77-89 | Ploidy/shapes/autopolyploidy/banding/syndrome/notation/dosage, sparrow, translocation; C26,C34-C39 |
| p10-11, Q90-100 | Hardy-Weinberg and founder count, topology/matrix, relatedness/loops/coefficient; C40-C43 |
| p12, SA1-2 | Seven-gene deletion ordering; enumerate all HLA genotypes; C11,C33 |
| p13-15, SA3-5 | Gametes/five-gene Punnett/counts; matrix completion/tree drawing; narrative pedigree/carriers/inbreeding; C13-C14,C21,C42-C43 |
| p16, Fun 1-4 | Star Wars, princesses, birthday riddle, relativity; excluded bonus |

### 2019 midterm

[2019_GENETICS_MIDTERM.md](../ARTIFACTS/2019_GENETICS_MIDTERM.md), 14 PDF pages.

| Location | Content accounted for |
| --- | --- |
| p1-3, Q1-23 | Genetic code, mutant screen/classical discoveries/disorder definition, DNA percentages/complement/transcription/nucleotide/overhang, PCR/groove/Tm/palindromes; C01,C04-C07 and historical register |
| p3-4, Q24-37 | Circular digests, Southern probes, HLA, blood-test matching including invalid control, gels; C08-C11 and historical Southern |
| p5-7, Q38-76 | Monohybrid and multilocus counts, disease probabilities/grandchild carrier, epistasis ratios, dominance, pedigrees, ABO, gamete/chromosome combinations; C12-C21 |
| p8-10, Q77-100 | Specific genotype probability, mitosis micrograph, homologs, XLR/Y transmission and inference, AD + XLR, multinucleation, binomial, grandson risk, chi-square; C14,C21-C24,C27-C30 |
| p11, SA1 | Cystic-fibrosis narrative pedigree, exclusion evidence, obligate carriers and conditional carrier probability; C21 |
| p12, SA2-3 | Fly XX/XY/XXY/XO fertility/sex and intersex; PCR primers; C39 and historical primer design |
| p13, SA4 | Punnett construction plus metabolic epistasis/F2/testcross; C18 |
| p14, Fun 1-4 | Princesses, surgeon riddle, nugget counts, parking puzzle; excluded bonus |

### 2019 final

[2019_GENETICS_FINAL.md](../ARTIFACTS/2019_GENETICS_FINAL.md), 18 PDF pages;
DOCX and ODT corroborate the additional draft material as well as the main exam.

| Location | Content accounted for |
| --- | --- |
| p1-2, Q1-18 | Mutant screen/classical experiment/gene product, Tm/complement/HLA/Chargaff, Southern/PCR/palindromes/overhang; C04-C07,C11 and historical register |
| p3-5, Q19-47 | Digests/typing/gels, Mendel/disease patterns/unique gametes/epistasis, cell-cycle/binomial/life cycle/sex systems; C08-C10,C12-C18,C27-C28 |
| p6, Q48-55 | ABO + XLR combined zygosity/probability and transfusion compatibility; C16,C23-C24, partial as in 2018 |
| p7-9, Q56-76 plus XXX | Three-point mapping/interference, fly F2/reverse inference, tetrad parental phase/category, deletion ordering; C22,C31-C33. XXX is an additional unnumbered parental-type item |
| p9-10, Q77-92 | Ploidy/shapes/autopolyploidy/banding/Turner/notation/dosage, sparrow, translocation, Hardy-Weinberg/founder allele count; C26,C34-C40 |
| p11, malformed Q93 then Q94-100 | Matrix/tree, half-sibling pedigree relationship/common ancestor/loop/coefficient and homozygosity effect; C40-C43 |
| p12, SA1-2 | Eight-gene deletion ordering; translocation gamete enumeration/proportions/classification/viability; C33,C36 |
| p13-15, SA3-5 | Full multilocus cross, matrix/tree construction, narrative consanguineous pedigree/carriers/inbreeding; C13-C14,C21,C42-C43 |
| p16-17, extra SA1-2 | Draft sparrow absent-gene/stripe/beak count model with writer note; Z-linked lethal pigeon cross; C25-C26. These are present content, but not safely counted as administered questions |
| p18, Fun 1-4 | Socks, film descriptions, riddle, relativity; excluded bonus |

### 2025 midterm

[2025_GENETICS_MIDTERM.md](../ARTIFACTS/2025_GENETICS_MIDTERM.md), 13 PDF pages.

| Location | Content accounted for |
| --- | --- |
| p1-2, Q1-20 | Disorder/terminology matching, nutrient rescue, DNA percentages/structure/complement/nucleotide, palindromes/cut/overhang; C01-C03,C05-C07 |
| p2-3, Q21-29 | Finite-fragment digests, paternity/forensic gels, blood typing/invalid control, HLA; C08-C11 |
| p4-5, Q30-55 | Mendel/crosses, unique counts, albinism independence, dominance/disorder inference, epistasis/F2-testcross/ratio matching, chromosome-combination count; C12-C18 |
| p6-7, Q56-80 | Dominance displays, pedigrees, ABO, lethal survival, roan probability, Z-linked codominance, interaction vocabulary, recessive disease probability, mitosis/meiosis/sex systems; C15-C18,C20,C25,C28 |
| p8, Q81-84 | Reverse fly-parent inference; AR + XLR mutation/carrier probability and grandson; C22,C24 |
| p8-9, Q92-100 | Plant-cross hypothesis/expected count, then rabbit sex-ratio chi-square calculation/table/conclusion; C30. Q85-91 are absent, not silently reconstructed |
| p10, SA1 | Z-linked lethal pigeon cross and sex-specific survival/carriers; C25 |
| p11, SA2 | Four-generation family narrative, consanguinity, pedigree drawing, pattern exclusion, obligate carriers, Kathy's carrier probability; C20-C21. No inbreeding coefficient is requested |
| p12, SA3 | Epistasis with incomplete dominance, full Punnett square, phenotype assignment, F2 and testcross ratios; C19 |
| p13, Fun 1-4 | Princesses, Jon Snow, nugget counts, parking puzzle; excluded bonus |

### 2025 final

[2025_GENETICS_FINAL.md](../ARTIFACTS/2025_GENETICS_FINAL.md), 18 PDF pages.

| Location | Content accounted for |
| --- | --- |
| p1-2, Q1-20 | Chromosomal disorders, nutrient rescue, DNA percentages/structure/complement, cut/overhang/palindromes, finite-fragment vs long-strand digestion; C01,C03,C05-C08 |
| p3, Q21-25 | Gels, AB+ agglutination, two- and three-locus HLA; C09-C11 |
| p4-6, Q26-55 | Cross/ratio identification, unique counts, Mendel, epistasis, mitosis/meiosis, chromosome combinations, dominance diagrams/roan probability, ABO inference; C12-C18,C28 |
| p7, Q56-63 | Z-linked codominance, sex systems, karyotype stage, sparrow sex/stripe; C25-C26,C28 |
| p8-9, Q64-74 | Chi-square workflow, reverse fly-parent inference, recombination ceiling and two-point cis/trans/parental types/distance; C22,C30-C31 |
| p10-11, Q75-91 | Three-point parental/DCO/recombinant/distance, tetrad parental phase/categories, fly/human XXY, deletion notation, translocation products and ploidy; C31-C32,C34,C36,C38-C39 |
| p12-14, Q92-100 | Adjacent-1/adjacent-2/alternate classification, Robertsonian trisomy outcome, topology equivalence and matrix-to-tree selection; C36-C37,C41-C42 |
| p15, SA1 | Narrative consanguineous pedigree, pattern evidence, obligate carriers and conditional carrier probability; C20-C21. No inbreeding coefficient requested |
| p16, SA2 | Ten-gene deletion order with English-word answer and working guidance; C33 |
| p17, SA3 | List gametes/testcross genotypes, construct Punnett square, count unique outcomes; C13-C14, constructed reasoning |
| p18, Fun 1-4 | Princesses, Jon Snow, nugget counts, parking puzzle; excluded bonus |

## Source cautions before reuse

These observations affect interpretation and adaptation. They do not call for editing the archived
exams, and the searchable copies preserve the supplied wording.

- **2025 M numbering:** Q84 is followed by Q92 in PDF, DOCX, and ODT text. Do not report an
  extractor loss or manufacture Q85-91 from a stated total of 100.
- **2025 M chi-square data:** the p9 story says 44 males/56 females while the table uses 39/61.
  Those give different test statistics; use one internally consistent data source in a future item.
- **2025 M Q82-84:** David is described as a CF carrier although his mother is wild type for both
  diseases; this alone can be consistent through his father. Laura's unaffected phenotype with an
  affected mother supports CF-carrier inference. The phrase "her father had AIS" needs biological
  and reproductive-context review rather than literal reuse of the disease story.
- **ZW lethal wording:** 2019 F extra SA2 and 2025 M SA1 say embryos die with *two copies*, then ask
  about female survival and whether a living female can carry the allele. The stem must explicitly
  settle expression in a hemizygous ZW female. The intended hemizygous-lethal model cannot simply
  be assumed from that wording; preserve this ambiguity in the archive and fix it before adaptation.
- **2025 F Q11-12:** the setup names AatII but the questions name Bsp119I. This is a source defect,
  not a need for a second restriction-enzyme concept.
- **2025 F Q87:** "XXY triploid (3n)" mixes sex-chromosome constitution with whole-genome ploidy.
  A future fly-versus-human question needs an explicit autosomal complement and consistent model.
- **2019 F drafting residue:** p8 has an XXX item; p11 has a merged Q93 stem; p16 has writer notes
  and an additional sparrow problem whose setup and note use different parental descriptions.
  These pages show intended ideas, not validated final assessment items.
- **Older reuse hazards:** 2017/2018 F pedigree narratives label Barb with a male symbol; 2018 F
  Q92 calls lowercase f the dominant allele; 2017 F tetrad counts total 201 while the prompt says
  200. These do not alter the skill inventory but preclude blind copying.
- **Historical PCR primer source:** `M/pcr_design.py:96-99` calls the selected primers "RNA primers"
  despite producing DNA-letter sequences for PCR. Treat it as existing relevant implementation
  needing content review, not a fully endorsed ready-to-publish reuse.
- **Viability/probabilities:** older translocation SA asks for gamete percentages and viable zygotes.
  A future educational model must state its segregation and viability assumptions; six displayed
  gametes alone do not establish equal real-world probabilities or universal clinical outcomes.

## Verification and limits

- All nine PDF text streams were read; companion conversion includes every non-header text line,
  with deliberate character normalization and image-omission notes. PDF tables/formulas and
  images are not guaranteed to be fully reconstructible from Markdown.
- All six native files were converted for comparison. The PDF is the reference for displayed
  numbering; native conversion can restart lists and produce verbose HTML tables. Native checks
  corroborate the 2025 skipped numbers/short answers and the 2019 additional draft material.
- All 130 CSV rows were resolved to existing local source files. Coverage judgments inspect
  student prompts, modes, answer-format calls, key YAML entries and relevant shared helpers;
  targeted searches also checked nearby unlisted implementations.
- No complete generator run, fresh website build, LMS import, rendered BPQ-output comparison,
  or answer-key audit was performed. "Covered" means source-level educational overlap, not
  verified publication or a guarantee that every randomized instance is correct.
- No coverage percentage is reported: repeated years, varying points, optional short answers,
  restarted/missing numbering and mixed-granularity skills make a raw question-count percentage
  misleading. The block ledger and individual skill decisions provide the reviewable evidence.
- Search/cleanup/structure checks apply to the new Markdown. This documentation-only task does
  not require the full repository pytest suite.

## Configured task row map

CSV line numbers are one-based and include the header and blank separator rows. Ranges contain
all rows for the named topic, including any internal separators. Full paths are defined above.

| List | Topic | Lines | Configured rows |
| --- | --- | --- | ---: |
| genetics_tasks1.csv | genetic_disorders | 2-3 | 2 |
| genetics_tasks1.csv | dna_structure | 5-24 | 20 |
| genetics_tasks1.csv | dna_profiling | 26-34 | 9 |
| genetics_tasks1.csv | mendelian | 36-46 | 11 |
| genetics_tasks1.csv | gene_interactions | 48-65 | 15 |
| genetics_tasks1.csv | chromosomal_inheritance | 67-84 | 16 |
| genetics_tasks1.csv | chi_square | 86-93 | 8 |
| genetics_tasks2.csv | gene_mapping | 2-19 | 18 |
| genetics_tasks2.csv | chromosomal_disorders | 21-38 | 18 |
| genetics_tasks2.csv | population_genetics | 40-43 | 4 |
| genetics_tasks2.csv | phylogenetics | 45-53 | 9 |
