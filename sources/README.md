# Папка источников (корпус отчётов ИЦ «Технет» СПбПУ)

Сюда кладутся тексты отчётов, докладов, монографий и дайджестов для работы оптики
в режиме RAG-навигатора. Сам пакет их не содержит — вы добавляете файлы, на
которые у вас есть права (см. `USAGE_NOTICE.md`).

## Как подключить отчёты

1. Положите файлы PDF/DOCX в эту папку. Рекомендуемые имена — в поле `file`
   каждого источника в `../data/source_registry.json`. Например:
   - `arch_technet_2025.pdf`
   - `smart_manufacturing_2025.pdf`
   - `new_materials_2026.pdf`
   - `digests/technet_digest_01.pdf` … и т.д.
2. Если имя файла отличается — обновите поле `file` и переключите
   `text_available` в `true` в `../data/source_registry.json`.
3. После извлечения текста заполните `key_theses` и `locators` (раздел/страница)
   в `../data/reports_index.json`, чтобы модель могла точно цитировать.

## Правило работы модели

Пока текст отчёта не загружен (`text_available: false`), модель отвечает по
метаданным и помечает содержательные утверждения как «не найдено в загруженных
источниках». Это защищает от выдумывания цитат.

## Рекомендуемая структура

```
sources/
  arch_technet_2024.pdf
  arch_technet_2025.pdf
  roadmap_summary_2025.pdf
  navigator_2025.pdf
  regulation_2025.pdf
  smart_manufacturing_2025.pdf
  bvs_digital_testing_brics_2025.pdf
  composites_nuclear_2025.pdf
  bvs_composite_operation_2026.pdf
  new_materials_2026.pdf
  digests/
    technet_digest_01.pdf
    ...
```
