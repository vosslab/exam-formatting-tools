# Splitting matching YAML banks

Curate the full original matching YAML in BPQ. Keep a JSON mapping in this repository to select
which terms belong to each assessment block and override its metadata when needed. Generate the
split YAML files from those two inputs; do not edit the split files by hand.

[split_matching_yaml.py](../tools/split_matching_yaml.py) handles the mechanical split. Choosing
useful groups and polishing the original prompts and descriptions remain editorial work.

## Sources and generated outputs

- **Original BPQ YAML:** term keys, description variants, replacement rules, and default metadata.
  Make wording and factual corrections here, once.
- **Local JSON mapping:** group membership, output filenames, and optional per-group metadata
  overrides. Keep mappings under `task_files/matching_sets/` with the assessment recipes.
- **Generated split YAML:** local inputs for the existing matching generator. Regenerate after
  source or mapping changes; running the tool replaces previous outputs.
  Outputs go under `generated/matching_sets/`, ignored by Git; track only the JSON maps.
- **Generated assessment YAML and key:** the selected, shuffled questions for a classroom version.
  Save these together when you want to preserve that version while changing its print layout.

Keep the full reusable banks in BPQ, without maintaining duplicate `_a.yml` and `_b.yml` banks
there. The local JSON records the assessment-specific split. See the genetics mappings:

- [genetics_terminology_split.json](../task_files/matching_sets/genetics_terminology_split.json): 5+5 terms.
- [mendelian_genetics_terms_split.json](../task_files/matching_sets/mendelian_genetics_terms_split.json): 5+5 terms.

The recipes in [GENETICS_EXAM1.md](../assessment_styles/GENETICS_EXAM1.md) use those generated banks.

## Choose the groups first

1. List the terms needed for the assessment and divide them into meaningful groups.
2. Assign every source term exactly once. The tool rejects missing, repeated, or unknown keys.
3. Group by teaching purpose and useful distinctions, rather than equal sizes alone. Keep
   concepts together when distinguishing them is the reasoning you want to assess.
4. Check whether a small group makes the answers too obvious through elimination.

For example, [hypothesis_testing_terms_split.json](../task_files/matching_sets/hypothesis_testing_terms_split.json)
uses this 3+4 grouping:

| Group | Terms | Matching prompts |
| --- | --- | --- |
| Hypotheses and reference distribution | Null hypothesis, alternative hypothesis, degrees of freedom | 3 |
| Decision quantities | Test statistic, critical value, significance level, p-value | 4 |

This is an editorial choice, not a required grouping for other assessments.

## Define the JSON mapping

A mapping contains:

- `source`: original YAML path, relative to the JSON file; absolute paths also work.
- `source_revision`: optional BPQ comparison commit recorded in generated headers. Set it to the
  revision reviewed; the tool does not update it automatically.
- `splits`: objects with an `output` YAML filename, a `pairs` list of exact source keys, and
  optional `overrides`.

For example, one entry within `splits` can customize its metadata:

```json
{
  "output": "hypothesis_testing_terms_a.yml",
  "pairs": ["nullhyp", "althyp", "dof"],
  "overrides": {
    "items to match per question": 3,
    "key description": "hypothesis-testing term",
    "keys description": "hypothesis-testing terms",
    "value description": "definition",
    "values description": "definitions",
    "dbsubject": "Biostatistics"
  }
}
```

All six override fields are optional; omitted fields retain their source values. Override the
item count when the source count exceeds the split's terms. The tool copies `replacement_rules`,
all selected description variants, and other source fields into every output.

Preserve exact source keys in `pairs`, including intentional whitespace or replacement tokens.
A key such as `nullhyp` depends on the original replacement rules to display the formatted term.
Changing membership does not change the term's wording.

Keep one `matching pairs` mapping per generated YAML file. Naming mappings `matching pairs 1`
and `matching pairs 2` in the original does not create two questions in the existing generator.

## Polish the original wording

Review the original bank against each proposed group, including every description variant.

- Give each description one best matching term. Read it against the other terms in its group;
  broad statements can accidentally describe more than one answer.
- Keep descriptions short, direct, and scientifically accurate. Remove filler while retaining
  the conditions that distinguish the concepts.
- Use parallel wording where it helps comparison. Avoid length, grammar, repeated term names,
  or color patterns that reveal the answer without understanding the concept.
- Keep variants equivalent in meaning. Rewrite or remove an unsuitable variant in the original
  rather than relying on generation to select a better one.
- Use terminology and notation students have learned. For biostatistics, name the significance
  level alongside alpha and write null hypothesis alongside its symbol. Preserve established
  statistical term colors.
- Review copied `exclude pairs` and `unused choices` if present. The tool preserves them as
  authored; check that they still permit the requested groups and leave matches unambiguous.
- Check the stem and usage note against what students actually match and whether choices are
  used once or may remain unused. Use JSON metadata overrides for group-specific labels.

## Check upstream and regenerate

Before reusing an assessment, review changes to the original BPQ bank since the JSON mapping's
`source_revision`. In the BPQ checkout, substitute that revision and the original bank's path:

```bash
git diff BASELINE_COMMIT HEAD -- problems/matching_sets/SUBJECT/ORIGINAL.yml
git diff HEAD -- problems/matching_sets/SUBJECT/ORIGINAL.yml
```

The first command shows committed changes since review; the second shows staged and unstaged
edits. Review their teaching implications and update the JSON grouping if terms were added or
removed. Update `source_revision` to the BPQ commit reviewed. It records a review point, not a
pinned source version: generation always reads the current original file.

From this repository's root, regenerate the local split banks:

```bash
source source_me.sh && python3 tools/split_matching_yaml.py \
  -i task_files/matching_sets/hypothesis_testing_terms_split.json
```

Outputs always go under `generated/matching_sets/`, replacing existing generated files.
Correct wording in the original, then regenerate instead of merging split-file edits.

The Quiz 2 and Genetics Exam 1 build recipes regenerate their splits before generating questions.
Mapping errors stop the build before any questions are drawn.

## Generate and review the assessment

Add one `YMATCH` task row per split source file, following [USAGE.md](USAGE.md). Use
`{exam_root}/generated/matching_sets/NAME.yml` in the `input` cell: relative inputs otherwise
resolve against BPQ's problems directory. Set `--num-choices` to the file's full term count when
every term should appear, keeping it consistent with the JSON item-count override.

Running `--num-choices 3` and `--num-choices 4` against the same seven-term bank samples the
groups independently. It does not guarantee disjoint groups or complete coverage.

Generate assessment YAML, its separate key, DOCX, and PDF through the existing recipe. Check:

- Each split produces the intended term count, with no repeated or omitted source terms.
- The answer key matches the displayed prompts and descriptions after shuffling.
- Descriptions remain unambiguous; inspect multiple variants when the original offers them.
- Numbering remains continuous. Seven matching prompts still use seven answer rows and earn
  3.5 points under the shared scoring rule, regardless of the split.
- The rendered PDF keeps blocks readable and together, with enough writing space.

Save the final assessment YAML and its key together. Re-render that saved YAML for layout edits;
rerunning the generators draws new questions. Manual Writer layout adjustments, duplication, and
cut-sheet preparation can follow generation. Review the final print layout after those edits.
