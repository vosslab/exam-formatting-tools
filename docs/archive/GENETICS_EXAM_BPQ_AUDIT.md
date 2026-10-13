# Genetics exam content versus BPQ task coverage: audit

**Date:** 2026-10-13  
**Purpose:** Identify exam-tested concepts and question formats worth adding to the Biology Problems (BPQ) genetics question bank.

## Scope and evidence

Exam PDFs inspected: 2016 midterm and final; 2017 midterm; 2018 final; 2019 midterm and final; 2025 midterm and final (eight distinct exams). BPQ comparison sources: `genetics_tasks1.csv` and `genetics_tasks2.csv`, supplied as attachments. The 2019 and 2025 exam filenames are treated as course/version identifiers, not reliable PDF creation dates. Exam question numbers below are printed numbers; some PDF text extraction splits numbers from figures or resets numbering for bonus questions.

**Important limitation:** The two task CSVs are *configured generator inventories*, not the complete BPQ repository. An absent CSV entry means **not demonstrated in the supplied genetics tasks**, rather than proof that BPQ contains no implementation elsewhere. A script name is evidence of an intended topic, not proof of the generated questions' precise learning objective or working output. This audit does not execute generators or inspect the underlying Python/YAML source files. Coverage labels are consequently conservative.

## Executive assessment

The existing genetics task lists cover nearly all *major course chapters*. Most of the older and newer exam material aligns with listed generators, including restriction digestion, DNA profiling, Mendelian crosses, epistasis, pedigree inheritance, chi-square, linkage mapping, cytogenetics, Hardy-Weinberg, and phylogenetic trees. **The clearest expansion opportunities are specific conceptual and interpretive question families that are repeatedly examined but lack identifiable task entries.** Expanding those families is more valuable than creating another generic generator for an already represented chapter.

**Status key:** **Gap** = no clearly corresponding entry in the supplied task lists; **Partial** = adjacent generator exists but the exact exam skill is not established; **Covered (listed)** = task entry explicitly addresses the skill. Priorities reflect recurrence, teaching value, and likely reusability, not an automated question count.

## A. Highest-value gaps and partial coverage

| Priority | Exam-tested learning objective | Evidence from exams | BPQ task-list evidence | Assessment and suggested expansion |
| --- | --- | --- | --- | --- |
| High | **History of genetics experiments**: Griffith transformation; Avery, MacLeod and McCarty; Hershey-Chase; Beadle-Tatum | 2017 midterm Q11–14; 2018 final Q5; 2019 midterm Q6–9; 2019 final Q5 | `beadle_tatum-metabolic_pathway.py` models metabolic pathways, not scientist/discovery matching | **Gap:** matching scientists to discoveries and reasoning from classical experimental results. |
| High | **Genetic code**: redundancy, codons, what a gene encodes | 2017 midterm Q4; 2018 final Q6; 2019 midterm Q1; 2019 final Q6 | `dna_structure` YAMLs, but no explicitly named genetic-code task | **Gap/partial:** genetic-code concepts and gene-product distinctions. Check existing YAML content first. |
| High | **DNA melting temperature and base composition** | 2016 midterm Q4, Q6; 2016 final Q3–4; 2017 midterm Q5, Q18; 2018 final Q7; 2019 midterm Q11–12, Q19; 2019 final Q7, Q10 | `chargaff_dna_percent.py` explicitly covers base percentages; `dna_structure-biol_351.yml` is not specific | **Partial:** Chargaff covered; add/verify GC versus AT effects on DNA Tm. |
| High | **DNA helix structure interpretation**: major/minor grooves, structural illustrations, A/B/Z DNA | 2016 midterm Q13; 2016 final Q7; 2017 midterm Q19; 2018 final Q10; 2019 midterm Q18 | `dna_structure-biol_351.yml` may cover terminology | **Partial:** check YAML for helix-form recognition and diagram-based major/minor groove questions. |
| High | **PCR amplification and target fraction**: cycle count, target length, background genome | 2016 midterm Q7, Q9; 2017 midterm Q20; 2018 final Q13; 2019 midterm Q17; 2019 final Q13 | No PCR-specific task entry | **Gap:** numerical amplification fraction and core PCR principles. Distinguish ideal doubling assumptions from actual reaction yield. |
| High | **Southern blot probe localization after digestion** | 2017 midterm Q30–31; 2018 final Q11–12; 2019 midterm Q29–30; 2019 final Q11–12 | Restriction-digest generators present; no probe-hybridization generator | **Gap:** predict which restriction fragments are detected by a sequence-specific probe, not merely which fragments exist. |
| Medium | **General DNA/RNA synthesis and molecular biology vocabulary**: template-strand transcription, RNA uracil, transcription versus translation, 3′ elongation, PCR primers | 2016 midterm Q2–3, Q5, Q12; 2016 final Q6; 2017 midterm Q10; 2019 midterm Q14 | `rna_v_dna.yml`, `complementary_sequences.py`, `nucleotide_components.yml` | **Partial:** base pairing and RNA/DNA differences represented; verify transcription-from-template with strand direction and replication polarity. |
| Medium | **Basic lab method recognition**: gel migration direction, Southern versus Northern/Western, restriction enzyme definitions | 2016 midterm Q14–16; 2016 final Q8 | Gel interpretation and digestion generators present, but no named lab-method matching task | **Gap/partial:** compact technique-and-purpose matching, electric charge and migration. |
| Medium | **Chromosome and meiosis mechanism concepts**: cell-cycle replication, homologous chromosomes, meiotic products, mitosis versus meiosis | 2016 midterm Q60–61; 2017 midterm Q72, Q91; 2019 midterm Q82, Q90; 2025 midterm Q55, Q72 | `meiosis_prophase_1.yml`, `meiosis_terms.yml`, `mitosis_and_meiosis.yml` | **Partial:** concepts likely covered in YAML; verify chromosome-count and cell-cycle scenarios. |
| Medium | **Pedigree relatedness and inbreeding coefficient** | 2016 final Q87–90; 2019 final Q96–100 | Pedigree pattern generators cover inheritance mode; no named inbreeding-coefficient generator | **Gap:** common-ancestor tracing, valid inbreeding paths, coefficient calculation. |
| Medium | **DNA-profiling limitations and interpretation** | 2016 midterm Q17–18; 2016 final Q13–14; 2018 final Q26–27; 2025 midterm Q23–24; 2025 final Q21–22 | `who_father_html.py`, `who_killer_html.py` | **Covered (listed)** for visual matching. Inspect whether generators also address inconclusive results and why bands are shared. |
| Medium | **Chromosomal sex determination and dosage compensation**: Barr bodies, X inactivation, Turner, different sex-determination systems | 2016 final Q79–80; 2019 final Q84–86; 2025 final Q1–6 | `sex_determination.yml`, `cytogenetic_notation-disorders.py`, `cytogenetic_notation-aneuploidy.py` | **Partial:** syndromes and sex determination listed; check explicit Barr-body counting and X-inactivation questions. |
| Low | **Conceptual definition of gene/genome/genetics/genomics** | 2025 midterm Q5–8 | `genetics_terminology.yml`, `mendelian_genetics_terms.yml` | **Partial:** inspect YAML contents before adding another terminology bank. |
| Low | **Population genetics beyond Hardy-Weinberg arithmetic**: inbreeding consequences, interpretation of allele frequencies | 2016 final Q91–93; 2019 final Q90–92, Q100 | `hardy_weinberg_numeric.py`, `hardy_weinberg_mc_type.py`, `population_genetics_terms.yml` | **Partial:** Hardy-Weinberg listed; inbreeding consequences and assumptions need verification. |

## B. Major areas already represented in BPQ task lists

| Course/exam family | Representative exam evidence | Matching configured BPQ assets | Coverage judgment |
| --- | --- | --- | --- |
| Genetic disorders | 2025 midterm Q1–4; 2025 final Q1–6 | `genetic_disorders.yml`; cytogenetic notation disorder/aneuploidy scripts | Covered (listed); check specific disorder examples |
| Chargaff and complementarity | 2016 midterm Q1, Q4, Q11; 2025 midterm Q10, Q12 | `chargaff_dna_percent.py`, `complementary_sequences.py` | Covered (listed) |
| Restriction-site palindromes and overhangs | 2016 midterm Q19–24; 2025 midterm Q14–20 | `palindrome_sequence_match.py`, `overhang_sequence.py`, `overhang_type.py` | Covered (listed) |
| Linear and circular restriction maps | 2016 midterm Q26–33; 2018 final Q19–24; 2025 final Q17–20 | `linear_digest.py`, `circular_digest.py` across difficulty levels | Covered (listed); verify fragment-versus-band semantics |
| Blood typing and HLA haplotypes | 2016 final Q12; 2018 final Q9, Q25; 2025 final Q23–25 | `blood_type_agglutination_test.py`, `hla_genotype.py` | Covered (listed) |
| Paternity and forensic gels | 2016 final Q13–14; 2025 final Q21–22 | `who_father_html.py`, `who_killer_html.py` | Covered (listed) |
| Mendelian principles, monohybrid crosses, gametes | 2018 final Q32–37; 2025 final Q26–33 | `mendel_four_principles.yml`, `monohybrid_genotype_statements.py`, `punnett_choice.py`, `unique_gametes.py`, `unique_cross_genotypes.py`, `unique_cross_phenotypes.py` | Covered (listed) |
| Dominance, ABO, lethal alleles, epistasis | 2016 final Q29–31; 2018 final Q38 onward; 2025 midterm Q62–71 | `degrees_of_dominance.yml`, `blood_type_offspring.py`, `lethal_allele_survival.py`, `epistasis/*` | Covered (listed) |
| Autosomal and sex-linked pedigrees | 2016 midterm final pedigree exercise; 2018 final inheritance questions; 2025 midterm pedigree exercise | `pedigrees/*`, `dominant_and_X-linked_recessive.py`, `x_linked_reciprocal_cross.py` | Covered (listed) |
| Chi-square and inheritance testing | 2017 midterm Q93–100; 2019 midterm Q94–100; 2025 midterm Q92–100 | `chi_square_calculated.py`, `chi_square_choices.py`, `chi_square_hypotheses.py`, `chi_square_errors.py` | Covered (listed) |
| Recombination, gene order, two-/three-point mapping | 2016 final Q50–69; 2019 final Q59–76; 2025 final Chapter 8 | `two-point_test_cross-*`, `three-point_test_cross-*`, tetrad mapping scripts | Covered (listed) |
| Chromosomal rearrangements, deletions, polyploidy | 2016 final Q70–82; 2019 final Q77–89; 2025 final Chapter 9 | `deletion_mutants/*`, `translocation/*`, `polyploid/*`, `cytogenetic_notation/*` | Covered (listed) |
| Hardy-Weinberg | 2016 final Q91–93; 2019 final Q90–92 | `hardy_weinberg_numeric.py`, `hardy_weinberg_mc_type.py` | Covered (listed) |
| Gene trees and distance matrices | 2016 final Q83–86; 2019 final Q93–95; 2025 final Chapter 11 | `gene_tree_choice_plus.py`, `gene_tree_matches_plus.py` | Partial: tree selection listed; verify distance-matrix calculations and reconstruction |

## C. Question-design distinctions worth preserving

1. **Probe detection is not restriction digestion.** Existing digest scripts can teach fragment lengths. Southern blot problems require tracking which fragments contain the probe-binding site (2017 midterm Q30–31).
2. **A pathway screen is not historical-experiment literacy.** `beadle_tatum-metabolic_pathway.py` covers rescue/order logic. It does not establish coverage of Griffith, Avery-MacLeod-McCarty, or Hershey-Chase (2019 midterm Q6–9).
3. **DNA complementarity is not transcription.** The latter adds template orientation and U-for-T substitutions (2019 midterm Q14).
4. **Chromosome-disorder notation is not dosage compensation.** Karyotypes and syndrome names do not establish Barr-body/X-inactivation interpretation (2019 final Q84–86).
5. **A pedigree inheritance-pattern question is not an inbreeding calculation.** Shared ancestors and path-based coefficient computation are separate skills (2019 final Q96–100).
6. **A gene-tree choice is not necessarily a distance-matrix reconstruction.** The exams ask both (2016 final Q83–86).
7. **Single-select and multi-select differ.** The 2025 exams include multiple-correct nutrient-rescue and restriction-fragment questions (2025 midterm Q9, Q21–22; 2025 final Q7, Q17–20). Existing generator support for the actual response type should be checked rather than inferred from topic names.
8. **Image-dependent questions require visual review.** Restriction maps, gels, blood typing, helices, pedigrees, and tree diagrams cannot be validated solely from PDF text extraction.

## D. Proposed BPQ expansion order

**Wave 1: repeated, clearly unrepresented question families.** Add scientist/discovery matching; PCR amplification-fraction calculations; Southern blot probe detection. These recur across years and have no direct counterparts in the supplied CSVs.

**Wave 2: inspect existing YAMLs, then fill verified gaps.** Inspect `dna_structure-biol_351.yml`, `rna_v_dna.yml`, `genetics_terminology.yml`, `meiosis_terms.yml`, `sex_determination.yml`, and the gene-tree generators. Add only missing Tm, major/minor grooves, genetic-code redundancy, transcription orientation, Barr bodies, and distance-matrix tasks.

**Wave 3: advanced interpretation.** Add pedigree inbreeding-path/coefficient questions and selected conceptual laboratory-method questions if these remain useful for the present course. Preserve existing strong generators for mapping, inheritance, cytogenetics, and population genetics.

## E. Validation checklist before implementing new generators

- Read the actual Python/YAML behind every candidate overlap. Record whether it produces the *same student reasoning task*, not merely the same topic.
- Confirm the eight PDFs against their source ODT/DOCX where available. Those editable files and `genetics_exam_sources.tsv` were named in the request but **were not provided**. They are therefore not audited.
- For each confirmed gap, record one representative exam year/question number, expected input/figure, student action, and answer type.
- Distinguish recurring instructional questions from one-off student-authored/presentation questions in older finals. Do not create generators simply to reproduce a one-time question.
- Review scientific accuracy and current course relevance before adapting legacy wording. For example, older 'one gene = one polypeptide' wording is not a complete modern definition of a gene; 2025 final Q11–12 also switches the enzyme name within the stem and questions.
- Compare emitted BPQ examples visually with the original exam figures before declaring an image-based skill covered.

## F. Source inventory and remaining uncertainty

| Source | Pages | Audit status |
| --- | ---: | --- |
| `2016_genetics_midterm.pdf` | 13 | Exam PDF inspected |
| `2016_genetics_final.pdf` | 11 | Exam PDF inspected |
| `2017_genetics_midterm.pdf` | 13 | Exam PDF inspected |
| `2018_genetics_final.pdf` | 16 | Exam PDF inspected |
| `2019_genetics_midterm.pdf` | 14 | Exam PDF inspected |
| `2019_genetics_final.pdf` | 18 | Exam PDF inspected |
| `2025_genetics_midterm.pdf` | 13 | Exam PDF inspected |
| `2025_genetics_final.pdf` | 18 | Exam PDF inspected |
| `genetics_tasks1.csv`, `genetics_tasks2.csv` | n/a | Configured BPQ task inventories inspected |
| 2019/2025 ODT and DOCX sources; `genetics_exam_sources.tsv` | n/a | Not supplied, not inspected |
| BPQ Python/YAML implementations and generated output | n/a | Not supplied, not inspected |

**Conclusion:** This is a **document-to-task-inventory coverage audit**, not a source-code-verified complete BPQ audit. It identifies the most defensible next inspections and likely expansions without labeling existing BPQ functionality absent merely because a CSV filename does not mention it.
