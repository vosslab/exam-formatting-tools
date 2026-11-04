# Design decisions

<!-- VENDORED HEADER: START -->
Record each durable decision about how this code and repository are shaped, once it is settled, with
the reasoning a later reader needs. Guidance Neil Voss states belongs in
[HUMAN_GUIDANCE.md](HUMAN_GUIDANCE.md), dated history in `docs/CHANGELOG.md`, open discussion in
`docs/active_plans/decisions/`. [PROPAGATED HEADER - ENTRIES BELOW ARE YOURS]
<!-- VENDORED HEADER: END -->

Write each decision as a level-three heading with these four fields. `Owner` names the
authoritative code or contract document, rather than a person.

```markdown
### <decision title>

**Decision.** <the durable direction>

**Why.** <the reason it was chosen>

**Consequence.** <the constraint a future change preserves>

**Owner.** <the authoritative code or contract doc>
```

### Named document styles own reusable layout

**Decision.** Choice styles inherit compact spacing and an inset label origin from Choice;
question styles own question separation. Repeated boilerplate, labels, tables, and writing spacing
use named styles. Content-dependent markup, pagination, and image geometry remain explicit.

**Why.** Manual choice-style changes in LibreOffice should preserve typography and spacing.

**Consequence.** Emitters select styles instead of overriding reusable paragraph layout.
All picture insertion paths explicitly zero edge distances. PDF export stays DOCX-based.

**Owner.** [../ef_tools/docx_builder.py](../ef_tools/docx_builder.py) and
[../assessment_styles/exam_styles.yaml](../assessment_styles/exam_styles.yaml).
