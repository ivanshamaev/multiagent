# Review guide: лекция NNNN

Не completed receipt. JSON schema example содержит false flags.

## Inputs

Lecture ID, reviewer, UTC timestamp, digest и реально применённые skills.
Digest: `python -m course.check --digest N` после финальных corrections.

## Editorial pass

Полная вычитка, язык/structure/duplication/consistency findings.

## Technical pass

Claim location → primary source/code/evidence anchor → verified verdict и scope/date.

## Corrections и recheck

Finding → correction → recheck; major rewriting → full reread.

## Текстовая семантика схем и итог

Сверить Mermaid source, `accTitle`/`accDescr`, подпись и текстовый эквивалент
с техническими claims. Не делать скриншоты и browser/visual review.
Для новых лекций использовать schema v2 и `diagram_semantics: true` только после
такой текстовой проверки. Машинная сборка — отдельный static gate, не визуальная
вычитка. Без major/blocking unresolved findings; same-author passes не independent.
Исторические schema v1 receipts сохраняют фактически выполненные проверки.
