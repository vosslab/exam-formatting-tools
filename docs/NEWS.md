# News

## v26.09 - 2026-09-21

### Highlights

- Build a quiz or exam from a website task CSV with one generated question per resolved task.
- Keep table drawings, pedigrees, sequence strips, and other matching-prompt images in the YAML-to-DOCX workflow.
- Produce answer keys and consistent question numbering for BBQ, MAT, ORD, and matching blocks.
- Use the same conservative ZipGrade rules for validation and exam-mode candidate acceptance.

### Upgrade notes

- Converter scripts moved under `launchers/` in this release. Current commands use
  `python3 converters/<script>.py`; dedicated assessment recipes are in `builders/`.
- Task-CSV conversion uses the repository [../bbq_settings.yml](../bbq_settings.yml) by default; pass `-s` only when using another settings file.
