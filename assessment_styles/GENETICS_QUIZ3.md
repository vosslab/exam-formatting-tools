# Genetics Quiz 3

Twenty scored questions share two generated setups. The progression follows the historical
Quiz 3 artifacts: null hypothesis, row contributions, chi-square total, degrees of freedom,
critical value, p-value, and conclusion; then parental classes, double crossovers, recombinant
classes, three pairwise recombination frequencies, gene order, and observed double crossovers.
Part 1 also asks for a p-value interpretation and one progeny genotype probability.

Questions 13-15 each require two selections. Every question is one point; award those three
points only when both selections are correct. Interference and expected double crossovers
are outside this quiz's scope. Twenty questions describes the workload, not a validated timing
estimate.

## Generate next year's version

From the repository root, choose a new output folder:

```bash
bash builders/build_genetics_quiz3.sh generated/genetics_quiz3_2027
```

The recipe uses the same setup components as the standalone biology-problems generators:
`chisquarelib.create_observed_progeny` and `GeneMappingClass.setup_question`. It reuses their
table and phenotype renderers, then computes every subquestion and distractor from the shared
data. The sibling repositories are unchanged. Paths come from [../bbq_settings.yml](../bbq_settings.yml).
There is no parsing of rendered tables to recover answers.

The date defaults to today. To specify it, run the authoring step directly, then the common
DOCX/PDF converters:

```bash
source source_me.sh && python3 builders/make_genetics_quiz3.py \
    -o generated/genetics_quiz3_2027/quiz3.yaml -d 2027-11-02
```

Outputs stay together: `quiz3.yaml`, `quiz3_setup.json`, `quiz3-key.txt`, `quiz3_files/`,
`quiz3.docx`, and `quiz3.pdf`. Existing generation artifacts are preserved; use a new folder
to draw a fresh version. Generated course files remain ignored by Git.

## Reproduce a saved version

The setup JSON preserves counts, gene phase, order, distances, and source artwork. The saved
YAML preserves the final question and choice order. Rebuild from YAML to retain the exact quiz:

```bash
source source_me.sh && python3 converters/yaml_to_exam_docx.py \
    -i generated/genetics_quiz3/quiz3.yaml -o generated/genetics_quiz3/review.docx \
    --page-break-sections --keep-questions-together
bash converters/docx_to_pdf.sh generated/genetics_quiz3/review.docx generated/genetics_quiz3 300
```

To recompose the parts from the saved setup, pass `-i PATH/quiz3_setup.json` to the authoring
script and use a new output folder. Snapshot files are instructor-authored inputs: keep their
scientific values and saved table markup together. Inspect each new PDF before classroom use.

The outer-pair recombinant percentage can be smaller than the sum of the two adjacent map
intervals. Questions ask for observed recombination frequencies explicitly; reverse gene
orders are equivalent and never appear as competing answers.
