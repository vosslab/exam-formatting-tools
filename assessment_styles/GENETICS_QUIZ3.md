# Genetics Quiz 3

Twenty scored questions share two generated setups, followed by one additional progeny
probability question (21 points total). The progression follows the historical
Quiz 3 artifacts: null hypothesis, row contributions, chi-square total, degrees of freedom,
critical value, p-value, and conclusion; then parental classes, double crossovers, recombinant
classes, three pairwise recombination frequencies, gene order, and observed double crossovers.
Part 1 also asks for a p-value interpretation and one progeny genotype probability.

Calculation choices show the arithmetic and its evaluated result for calculator-free use.
Chi-square row and total choices share five calculation paths: observed minus expected divided
by observed, observed minus expected divided by expected, expected minus observed divided by observed,
squared deviation divided by observed, and the correct squared deviation divided by expected.
Each total repeats its path's displayed row values. Preserve A-E order across these questions
so students can carry an earlier choice through the calculation, including an incorrect one.
Mapping choices follow the setup generator's whole-number frequency contract, including
the distractors; fractional distractors are excluded rather than rounded into false equations.

Questions 13-15 each require two selections. Every question is one point; award those three
points only when both selections are correct. Interference and expected double crossovers
are outside this quiz's scope. The question count describes the workload, not a validated timing
estimate.

## Generate next year's version

The active quiz uses `generated/genetics_quiz3.*` files. From the repository root:

```bash
bash builders/build_genetics_quiz3.sh
```

The recipe uses the same setup components as the standalone biology-problems generators:
`chisquarelib.create_observed_progeny` and `GeneMappingClass.setup_question`. It reuses their
table and phenotype renderers, then computes every subquestion and distractor from the shared
data. The sibling repositories are unchanged. Paths come from [../bbq_settings.yml](../bbq_settings.yml).
There is no parsing of rendered tables to recover answers.

Chi-square sample sizes vary from 160 to 320 in multiples of 16, following the dihybrid
hypothesis generator's pattern. Expected counts come from the drawn total and 9:3:3:1;
observations use the shared sampler without forcing a biased ratio or a rejection outcome.

The date defaults to today. To specify it, run the authoring step directly, then the common
DOCX/PDF converters:

```bash
source source_me.sh && python3 builders/make_genetics_quiz3.py \
    -o generated/genetics_quiz3.yaml -d 2027-11-02
```

Outputs stay together: `genetics_quiz3.yaml`, `genetics_quiz3_setup.json`, `genetics_quiz3-key.txt`,
`genetics_quiz3_files/`, `genetics_quiz3.docx`, and `genetics_quiz3.pdf`. The builder refuses to overwrite existing generation artifacts.
When replacing the quiz, save any manual edits before removing that version's prefixed files
and media folder. To keep multiple versions, invoke the Python authoring step directly with a
distinct `-o` filename, then run the DOCX/PDF converters for that filename. Generated course files
remain ignored by Git.

## Reproduce a saved version

The setup JSON preserves counts, gene phase, order, distances, and source artwork. The saved
YAML preserves the final question and choice order. Rebuild from YAML to retain the exact quiz:

```bash
source source_me.sh && python3 converters/yaml_to_exam_docx.py \
    -i generated/genetics_quiz3.yaml -o generated/genetics_quiz3_review.docx \
    --page-break-sections --keep-questions-together
bash converters/docx_to_pdf.sh generated/genetics_quiz3_review.docx generated 300
```

To recompose the parts from a saved setup, save its JSON before
replacing the current quiz, then pass `-i PATH/genetics_quiz3_setup.json` to the authoring script.
Snapshot files are instructor-authored inputs: keep their
scientific values and saved table markup together. Inspect each new PDF before classroom use.

The outer-pair recombinant percentage can be smaller than the sum of the two adjacent map
intervals. Questions ask for observed recombination frequencies explicitly; reverse gene
orders are equivalent; the choices include reversed orientations with only one correct answer.
