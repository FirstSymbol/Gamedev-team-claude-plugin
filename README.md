# Studio — виртуальная IT/геймдев команда агентов для Claude Code

Плагин `studio`: оркестратор, 5 лидов и 23 специалиста. Каждая роль — это агент со своей
моделью и набором инструментов плюс скилл с базой знаний. Сильнее всего проработаны
**Unity** и **.NET**. Есть доменные модули: **iGaming/казино**, **мобильный F2P/LiveOps**,
**мультиплеер**, **PC/консоли**.

## Установка

Из GitHub (рекомендуется):
```powershell
claude plugin marketplace add FirstSymbol/Gamedev-team-claude-plugin
claude plugin install studio@studio-market --scope user
claude plugin list
```
Внутри сессии то же самое: `/plugin marketplace add FirstSymbol/Gamedev-team-claude-plugin`,
затем `/plugin install studio@studio-market`. Обновление: `claude plugin marketplace update studio-market`.

Из локальной копии:
```powershell
git clone https://github.com/FirstSymbol/Gamedev-team-claude-plugin.git
claude plugin marketplace add ".\Gamedev-team-claude-plugin"
claude plugin install studio@studio-market --scope user
```

После правок файлов пака перезапустите сессию или выполните `/reload-plugins`.
Чтобы попробовать пак без установки, запустите `claude --plugin-dir "<папка>\plugins\studio"`.

## Как пользоваться

| Что нужно | Как сказать |
|---|---|
| Любая задача для команды | «Команда studio, …» или просто опишите задачу: оркестратор сам выберет роли |
| Фича целиком (спека → код → тесты → ревью) | `/studio:feature ежедневный бонус с таймером` |
| Старт нового проекта | `/studio:kickoff идея: social casino с турнирами` |
| Баг | `/studio:bugfix <описание/лог>` |
| Готовность к релизу | `/studio:release 0.4.0 Android+iOS` |
| Статус | `/studio:status` |
| Ревью рисков | `/studio:risk-review` |
| Конкретная роль | «Используй агента studio:economy-monetization-designer …» |

Агенты пишут результаты в папку `.team/` в корне проекта: бриф, доска задач, риски, ADR,
спеки, хэндоффы и отчёты. Между собой агенты передают пути к файлам, а не содержимое.
Это экономит токены и даёт общую «память» команды.

## Состав команды

| Группа | Роли | Модель |
|---|---|---|
| Оркестрация | orchestrator (скилл главного потока) | модель сессии |
| Лиды | producer, product-manager, tech-lead-architect, lead-game-designer, qa-lead | Opus |
| Аналитика | business-analyst, system-analyst, data-analyst | Sonnet |
| Геймдизайн | game-designer, level-designer, narrative-designer, economy-monetization-designer | Sonnet |
| Арт/UX | ux-ui-designer, art-director, technical-artist | Sonnet |
| Разработка | unity-developer, dotnet-backend-developer, frontend-developer, multiplayer-network-engineer, devops-sre-engineer, security-engineer, code-reviewer | Sonnet |
| Качество/релиз | qa-engineer, release-platform-manager | Sonnet |
| Рынок/операции | marketing-manager, liveops-manager, compliance-advisor | Sonnet |
| Рутина | technical-writer | Haiku |

Иерархия: главный поток (оркестратор) → лиды → специалисты. Агенты могут вызывать других
агентов на глубину до 3 уровней. Мелкие задачи оркестратор отдаёт сразу одному специалисту,
без лида.

Общие скиллы: `team-protocol` (правила команды, подгружается в каждого агента),
`stack-unity`, `stack-dotnet`, `domain-igaming`, `domain-f2p-liveops`,
`domain-multiplayer`, `domain-pc-console`.

## Как устроена экономия токенов

1. **Постепенная подгрузка.** В контексте всегда лежат только короткие описания скиллов.
   Основной файл роли (SKILL.md) занимает не больше ~120 строк. Глубокие справочники
   (`references/*.md`) агент читает только по конкретному поводу.
2. **Командные сценарии скрыты** (`disable-model-invocation`): `/studio:feature` и другие
   не занимают место в контексте, пока вы их не вызовете.
3. **Изоляция контекста.** Каждый агент работает в своём окне и возвращает до 15 строк
   (STATUS/ARTIFACTS/…). Содержимое файлов обратно не пересылается.
4. **Модели по уровням.** Opus только у лидов, у исполнителей Sonnet, у рутины Haiku.
   Набор инструментов у каждой роли минимальный.
5. **Скрипты вместо обхода проекта.** `scan_unity_project.py` и `scan_dotnet_solution.py`
   дают сводку проекта в несколько десятков строк, вместо того чтобы агент читал сотни файлов.
6. **Английский внутри скиллов.** Токенов выходит примерно в 2–3 раза меньше, чем на
   русском. Отвечают агенты на языке пользователя.
7. **Правило «минимум ролей».** Оркестратор не зовёт роль, чей результат никому не нужен.
   Тривиальную задачу он делает сам.

Дополнительно можно скрыть описания редко используемых скиллов через `skillOverrides`
(`"name-only"`) в настройках и проверить стоимость контекста командой `/skill-doctor`.

## Режим Agent Teams (экспериментальный, по желанию)

Если специалистам нужно спорить между собой (например, GD ↔ экономист ↔ аналитик), включите
`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. Этот режим работает только в интерактивной сессии и
дороже по токенам. Учтите, что в нём участники игнорируют поле `skills:`. Каждый агент тогда
сам вызывает свой скилл: это прописано в теле агента.

## Структура

```
.claude-plugin/marketplace.json     локальный маркетплейс
plugins/studio/
  .claude-plugin/plugin.json
  AUTHORING.md                      стандарт оформления скиллов (бюджеты, структура)
  agents/*.md                       28 агентов-ролей
  skills/<роль>/SKILL.md            плейбук роли
  skills/<роль>/references/*.md     глубокая база знаний
  skills/<роль>/templates/*.md      шаблоны артефактов
  skills/team-protocol/scripts/     сканеры проекта и статус команды
tests/
  validate_pack.py                  проверка структуры и бюджетов
  run_triggers.py + trigger_cases.json   проверка маршрутизации (RU/EN запросы)
  sandbox/                          тестовый .NET 10 + Unity-подобный проект
```

## Тесты

```powershell
python tests/validate_pack.py --strict              # структура, бюджеты, ссылки
claude plugin validate "plugins/studio"             # официальный валидатор
python tests/run_triggers.py --jobs 4               # маршрутизация (тратит токены)
```

## Как добавить роль

1. Прочитайте `plugins/studio/AUTHORING.md`.
2. Создайте `skills/<role>/SKILL.md` (+ `references/`) и `agents/<role>.md`.
3. Добавьте роль в таблицу маршрутизации `skills/orchestrator/SKILL.md`, в `ROSTER`
   в `tests/validate_pack.py` и в раздел Roster в `AUTHORING.md`.
4. Запустите `python tests/validate_pack.py --strict`.

## Ограничения

- Юридические выводы (`compliance-advisor`, `domain-igaming`) носят справочный характер.
  Решения go/no-go должен принимать юрист.
- Unity Editor агенты запустить не могут, если он не установлен или не подключён MCP.
  Компиляцию и PlayMode-проверки в этом случае нужно делать вручную или в CI (см. `stack-unity`).
- Требования сторов, консолей и законы быстро меняются. Пункты с пометкой `(verify: …)`
  нужно проверить по первоисточнику.
