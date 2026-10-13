# Genetics Exam 1 selection

The draft selection is [genetics_exam1.csv](../task_files/genetics_exam1.csv).
It covers the content of the local Quiz 1 and Quiz 2 task files plus the website's
`task_files/genetics_tasks1.csv`, through Chapter 7: Chi Square Analysis.
This is a coverage draft for editing, with no instructor-specified length or point total yet.
Shared formatting, numbering, matching, and ZipGrade rules are in [EXAM_STYLE.md](EXAM_STYLE.md).

## Recorded draft status

The latest October 12 rebuild includes all 53 selected blocks with zero skips:
93 numbered rows on 22 PDF pages. ZipGrade validation passed. The circular-digest
page was visually checked; cuts at 1, 5, and 11 kb give bands 4, 6, and 2 kb,
matching the key A/C/E in its consecutive 2-6 kb answer bank.
Linear fragment and strand digests retain medium difficulty and request five choices,
in a consecutive range containing every correct band and at least one distractor. Punnett-square selection requests five choices and
omits the most distant parental-genotype distractor (randomly breaking ties).
Chi-square calculation/decision is excluded because it was not covered for this exam.

Circular digestion now also requests five consecutive choices at medium difficulty.
Enumeration finds 38 valid medium circular maps, with bands {2,4,6} or {3,4,5}.
Medium linear fragments fit five choices on 76 maps, but always yield {1,2,4,5};
retain medium for this exam per instructor preference, with this predictable answer-set
limitation recorded. The default score line counts rows; final grading weights are unset.

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
| Forward and inverse epistasis test-cross ratios | Forward direction |
| Original and varied combined autosomal/X-linked crosses | Varied crosses |
| Numeric chi-square calculation and calculation/decision MC | Excluded; not covered for this exam |

Fragment, strand, and circular digests remain distinct: the endpoints and wraparound affect
which lengths are counted. Paternity and forensic profiles remain distinct applications.
Definition matching and application questions remain when they test different reasoning.
The four Mendelian terminology banks cover general genetics, cross terminology, Mendel's
principles, and trait/genotype vocabulary; the cross-outcome bank tests predicted offspring.

## Build this selection

Run `bash builders/build_genetics_exam1.sh`. See [USAGE.md](../docs/USAGE.md) for the build outputs
and instructions for preserving edited questions. The source task CSV is the selection recipe;
the generated YAML is the editable question content, and `genetics_exam1-key.txt` is its key.
Compare the produced task blocks with this selection, and review the build skip report.
