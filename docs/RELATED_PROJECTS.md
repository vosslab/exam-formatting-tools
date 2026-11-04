# Related projects

Visitors use this repository to turn biology question-bank sources into printable, image-aware exams. The projects below support upstream authoring, adjacent delivery, or the same conversion workflow.

## Confirmed related projects

### qti-package-maker

- Relationship: companion/interoperability tool
- Link: https://github.com/vosslab/qti-package-maker
- Why visitors may care: It turns question banks into BBQ text and other assessment formats; this repository can turn saved BBQ text into printable exam YAML and DOCX.
- Evidence: [bbq_to_exam_yaml.py](../converters/bbq_to_exam_yaml.py) accepts BBQ input, [bbq_settings.yml](../bbq_settings.yml) passes the sibling checkout to task-generator subprocesses, and the [official README](https://github.com/vosslab/qti-package-maker) documents its BBQ and exam-YAML outputs.

### biology-problems

- Relationship: upstream content source
- Link: https://github.com/vosslab/biology-problems
- Why visitors may care: It provides the biology generator scripts that task-CSV workflows run to produce one question per task for a quiz or exam.
- Evidence: [bbq_tasks_to_exam_yaml.py](../converters/bbq_tasks_to_exam_yaml.py) resolves generator paths from [bbq_settings.yml](../bbq_settings.yml); the [official README](https://github.com/vosslab/biology-problems) documents standalone biology question generators and their BBQ/QTI outputs.

### biology-problems-website

- Relationship: same-workflow implementation
- Link: https://github.com/vosslab/biology-problems-website
- Why visitors may care: Its task CSV and alias settings are the input contract for batch-selecting biology generators before printing the resulting exam.
- Evidence: [bbq_tasks.py](../ef_tools/bbq_tasks.py) explicitly mirrors the website task-CSV contract; the [official README](https://github.com/vosslab/biology-problems-website) describes downloadable question banks and teaching workflows.

## Possible related projects

### 1EdTech QTI specification

- Relationship: domain standard/resource
- Link: https://www.1edtech.org/standards/qti/index
- Why visitors may care: Instructors who also move a question bank between LMSs can use the QTI specifications to understand the interchange formats produced by qti-package-maker before bringing BBQ content into this print workflow.
- Evidence: The [1EdTech QTI overview](https://www.1edtech.org/standards/qti/index) defines QTI as an exchange format for assessment content; qti-package-maker's [official README](https://github.com/vosslab/qti-package-maker) lists QTI exports alongside BBQ and exam YAML.
- Confidence: medium; this repository does not itself write QTI packages.

## Evidence notes

The confirmed entries are supported by current local converter/configuration references and their official project documentation. The QTI entry is an adjacent standards resource, not a runtime dependency or a DOCX formatting component. Searches for general DOCX/PDF exam converters found no additional project with a documented, direct relationship to this biology-question and BBQ/task-CSV workflow.
