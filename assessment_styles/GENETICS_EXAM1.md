# Genetics Exam 1 selection

The draft selection is [genetics_exam1.csv](../task_files/genetics_exam1.csv).
It selects Chapters 1-6 from the local Quiz 1 and Quiz 2 task files and the website's
`task_files/genetics_tasks1.csv`. Chapter 7 is excluded at the instructor's request.
Only question families students encountered in homework are eligible. Plan within 100 ZipGrade rows;
the instructor reviews the rendered exam before sending it to students.
Shared formatting, numbering, matching, and ZipGrade rules are in [EXAM_STYLE.md](EXAM_STYLE.md).

## Recorded draft status

The October 12 expanded draft includes 49 Chapter 1-6 blocks and 86 numbered rows.
The original 47 question objects are preserved; two additions add a second random metabolic
pathway and the inverse epistasis ratio question. One five-pedigree matching block remains.
Fourteen ZipGrade rows remain available. The two added tasks generated with zero skips.
The saved DOCX/PDF is regenerated (20 PDF pages); ZipGrade validation and continuous
answer-key numbering 1-86 pass. The instructor performs the final visual review.

Linear fragment and strand digests retain medium difficulty and request five choices,
in a consecutive range containing every correct band and at least one distractor. Punnett-square selection requests five choices and
omits the most distant parental-genotype distractor (randomly breaking ties).
All Chapter 7 chi-square questions are excluded because they are not on this exam.

Circular digestion now also requests five consecutive choices at medium difficulty.
Enumeration finds 38 valid medium circular maps, with bands {2,4,6} or {3,4,5}.
Medium linear fragments fit five choices on 76 maps, but always yield {1,2,4,5};
retain medium for this exam per instructor preference, with this predictable answer-set
limitation recorded. The expanded answer sheet uses 86 rows.

## Selection rules

- This selection uses four pairs in ordinary term-matching blocks.
- Use a single full-pattern pedigree MATCH block, with five patterns, in Chapter 6.
  It replaces the autosomal-only Chapter 5 block and the alternative pedigree MC tasks.
- Use medium difficulty where available, retaining different reasoning tasks within a family.
- Keep Unique Gametes, Unique Offspring Genotypes, and Unique Offspring Phenotypes consecutive
  as three independent questions.

## Overlap decisions

| Website alternatives | Draft selection and coverage |
| --- | --- |
| Matching and WOMC forms | MATCH only |
| Directionless and 5'/3' DNA complements | 5'/3' includes base pairing and direction |
| End type and overhang type | Overhang type includes blunt ends and both overhang directions |
| Easy, medium, rigorous, and bonus variants | One difficulty for each selected reasoning task |
| Two- and three-marker HLA | Three-marker HLA |
| Autosomal-only and full pedigrees, both MC directions | Full-pattern pedigree matching |
| Forward and inverse epistasis test-cross ratios | Both directions |
| Original and varied combined autosomal/X-linked crosses | Varied crosses |
| All Chapter 7 chi-square tasks | Excluded; not on this exam |

Fragment, strand, and circular digests remain distinct: the endpoints and wraparound affect
which lengths are counted. Paternity and forensic profiles remain distinct applications.
Definition matching and application questions remain when they test different reasoning.
The four Mendelian terminology banks cover general genetics, cross terminology, Mendel's
principles, and trait/genotype vocabulary; the cross-outcome bank tests predicted offspring.

## Historical midterm coverage audit

Compared the actual October 12 generated questions with
`ARTIFACTS/2025_genetics_midterm.pdf`, including its short-answer section.
This comparison preceded the later archive import and applies only to the 2025 midterm.
Historical references below use its printed question numbers; current-question references
in this historical table refer to the original 84-row draft.

Core DNA structure, restriction digestion, DNA profiling, HLA inheritance, Mendelian
principles, independent-assortment counts, lethal alleles, dominance definitions,
epistasis, pedigree pattern recognition, X-linked crosses, and meiosis remain represented.
Chapter 7 and all chi-square content are intentional exclusions.

| Historical content | Current coverage and gap |
| --- | --- |
| Q66 and short answer 1: Z-linked crosses, offspring sex, survival | Q81 names the ZW system; no Z-linked cross or sex-specific survival calculation |
| Short answer 2: draw a pedigree, justify inheritance, identify carriers, calculate carrier risk | Q62-66 identify patterns; no pedigree construction, obligate-carrier selection, or conditional carrier probability |
| Q84: infer a daughter's carrier risk, then her son's risk | Q68 combines two inheritance modes for one generation; no uncertain-carrier transmission through another generation |
| Q30-31, 41-43, 46, 48-53: identify test crosses, choose dihybrid parents, derive F1/F2 ratios | Q41-47 sample other monohybrid crosses. Q59-61 use or supply dihybrid ratios; basic F2 genotype ratio and test-cross purpose are not directly asked |
| Q40 and 71: next-child recessive disease probability | Q67 states independence in a sex-count problem; no direct next-child disease-risk question |
| Q55: convert diploid chromosome count to gamete combinations | Q48 counts gametes from explicit gene genotypes; no chromosome-count version |
| Q65: codominant offspring proportions | Definitions remain, but Q58 samples incomplete dominance. Q71 supplies a related X-linked heterozygote-proportion task, not an autosomal codominant cross |
| Short answer 3: combine epistasis and incomplete dominance to derive an unfamiliar ratio | Q59-61 cover standard gene interactions, not this combined case |
| Q63: infer ABO parent genotype/type from several children | Q52 uses one child; Q53 predicts possible offspring types, not inference from multiple siblings |
| Q25-28: ABO/Rh panel matching, including an invalid control | Q21 asks only for O-negative; invalid-control recognition and positive Rh interpretation are not directly assessed |

Sampling gaps within selected matching banks also matter: old Q5-8 included genome
and genomics, but current Q25-28 omit both; old Q73-76 included synapsis and chiasmata,
but current Q76-79 omit both. Current Q72-75 mention the pairing process and chiasmata
as stage clues, so that content is partial rather than wholly absent. The test-cross
term is also absent from the sampled cross-terminology block. Bank selection alone
does not guarantee these terms appear in a generated exam.

The earlier historical-gap expansion proposal is withdrawn: historical content is not an
addition candidate unless it belongs to the assigned homework. Use the catalog audit below
as the coverage boundary.

## Homework catalog coverage audit

Compared all 73 Chapter 1-6 task entries in
`../biology-problems-website/task_files/genetics_tasks1.csv` with the exam task selection
and saved question objects. Ignore the catalog's eight Chapter 7 entries by instruction.
Catalog entries include multiple difficulties and alternative formats; they are not 73
independent content requirements.

| Chapter | Homework task entries | Exam blocks | Answer rows | Coverage |
| --- | --- | --- | --- | --- |
| 1: Genetic disorders | 2 | 2 | 5 | Both families: disorder matching and pathway rescue |
| 2: DNA structure | 20 | 12 | 15 | Every family; collapse difficulty levels and overlapping end/direction variants |
| 3: DNA profiling | 9 | 4 | 4 | All four families; one blood test, HLA, paternity, and forensic profile |
| 4: Mendelian genetics | 11 | 11 | 26 | Every catalog entry represented |
| 5: Gene interactions | 15 | 10 | 13 | All non-pedigree families, both epistasis directions, two metabolic pathways; pedigrees covered in Chapter 6 |
| 6: Chromosomal inheritance | 16 | 10 | 23 | All major families; consolidate pedigree formats and fixed/varied combined-inheritance scenarios |
| Total | 73 | 49 | 86 | No major homework family omitted |

Specific consolidation decisions:

- Prime-labeled complementary sequences include direction and base pairing; overhang-type
  questions include blunt versus sticky ends as well as overhang direction.
- Retain separate linear fragment, linear strand, and circular digest tasks at medium level.
- Three-marker HLA replaces the two-marker variant; medium profiles replace easy/hard copies.
- One full-pattern matching block covers five inheritance modes, including the autosomal
  subset from Chapter 5. The catalog lists matching at easy level and medium pedigree-to-pattern
  MC; the exam's medium matching setting is an intentional difficulty/format combination.
- The varied combined autosomal/X-linked generator replaces the fixed original scenario.
- Include both F2-to-test-cross and test-cross-to-possible-F2 epistasis questions.
- Both metabolic tasks opt into random pathway selection with `--random`; no interaction or ratio is pinned in
  the CSV. Repeated interaction types remain possible and are reviewed by the instructor.
  The generator's default batch mode cycles through interactions for even coverage.

Coverage depth still varies. Chapter 3 has only four rows. Four-term matching samples do
not exhaust broad banks: genome/genomics and the test-cross term were absent from the
saved draft, and synapsis/chiasmata were represented only indirectly in stage clues.
Additional rows should sample existing homework families or additional terms, not introduce
Z-linked crosses, pedigree carrier-risk calculations, or other historical-only tasks.
The single five-pedigree matching block is the instructor's chosen coverage; do not add a
second block based on the earlier tentative discussion.

## Build this selection

Run `bash builders/build_genetics_exam1.sh`. See [USAGE.md](../docs/USAGE.md) for the build outputs
and instructions for preserving edited questions. The source task CSV is the selection recipe;
the generated YAML is the editable question content, and `genetics_exam1-key.txt` is its key.
Compare the produced task blocks with this selection, and review the build skip report.
