# Related projects

Visitors use this repository to turn biology question-bank sources into printable, image-aware exams. The projects below support upstream authoring, adjacent delivery, or the same conversion workflow.

## Confirmed related projects

### qti-package-maker

- Relationship: companion/interoperability tool
- Link: https://github.com/vosslab/qti-package-maker
- Why visitors may care: It produces the BBQ text and shared assessment formats consumed by this repository, and it supplies the table-image renderer used by the BBQ converters.
- Evidence: The local [INSTALL.md](INSTALL.md), [bbq_to_exam_yaml.py](../launchers/bbq_to_exam_yaml.py), and [../pip_extras.txt](../pip_extras.txt) identify the sibling import; the project's official README describes BBQ, QTI, HTML, and exam-YAML outputs.

### biology-problems

- Relationship: upstream content source
- Link: https://github.com/vosslab/biology-problems
- Why visitors may care: It provides the biology generator scripts that task-CSV workflows run to produce one question per task for a quiz or exam.
- Evidence: The local [bbq_tasks_to_exam_yaml.py](../launchers/bbq_tasks_to_exam_yaml.py) resolves generator paths from [../bbq_settings.yml](../bbq_settings.yml); the official project documents standalone biochemistry, genetics, molecular biology, and related question generators.

### biology-problems-website

- Relationship: same-workflow implementation
- Link: https://github.com/vosslab/biology-problems-website
- Why visitors may care: Its task CSV and alias settings are the input contract for batch-selecting biology generators before printing the resulting exam.
- Evidence: The local [bbq_tasks.py](../ef_tools/bbq_tasks.py) mirrors the website task contract, and the official repository exposes the `bbq_control` task and settings directories.

## Evidence notes

The relationship claims combine current local imports, launcher help text, [../bbq_settings.yml](../bbq_settings.yml), and the official repositories linked above. The external projects remain useful because they define content or interchange formats consumed by this pipeline, not merely because they use Python.
