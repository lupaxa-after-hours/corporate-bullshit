<p align="center">
  <a href="https://github.com/lupaxa-after-hours">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/after-hours/readme-logo.png" alt="After Hours" />
  </a>
</p>

<h1 align="center">Corporate Bullshit</h1>

Generate convincingly meaningless corporate language. Statements, meeting
lines, excuses, strategies, mission text, emails, jargon, translations,
bingo cards, and whole documents. The humour is the jargon. The grammar
stays intact.

It runs entirely offline. No API keys, no model, and no network. Python
3.11+ and the standard library are enough.

The PyPI name is `lupaxa-corporate-bullshit`. The import path is
`lupaxa.corporate_bullshit`. The console script is `corporate-bullshit`.
`lupaxa` is a namespace package — there is no `lupaxa/__init__.py`.

## What it Does

Each command fills sentence templates from a built-in vocabulary. Intensity
changes the words and the sentence shapes, not just the length.

| Level | Voice                                                 |
| ----- | ----------------------------------------------------- |
| 1     | Mild corporate language. Mostly understandable.       |
| 2     | Heavy jargon. This is the default.                    |
| 3     | Maximum nonsense. Extra buzzwords and longer clauses. |

Pass `--seed` when you want the same line again. The same seed, the same
arguments, and the same vocabulary version produce the same text. Company
names, recipients, and senders are copied through as literal text.

## Install

```bash
pip install lupaxa-corporate-bullshit
```

## Commands

```bash
corporate-bullshit generate --level 3
corporate-bullshit meeting --type avoidance
corporate-bullshit excuse --topic deadline
corporate-bullshit strategy --count 5
corporate-bullshit mission --company "Acme Corp"
corporate-bullshit email --type followup
corporate-bullshit jargon --define synergy
corporate-bullshit translate "We need more money"
corporate-bullshit bingo --size 5
corporate-bullshit document --type strategy
```

| Command     | What it Writes                                                                                 |
| ----------- | ---------------------------------------------------------------------------------------------- |
| `generate`  | Standalone statements for slides, meetings, and reports.                                       |
| `meeting`   | A contribution that agrees, avoids, deflects, follows up, strategises, objects, or summarises. |
| `excuse`    | A professional reason that a deadline, budget, report, or other task slipped.                  |
| `strategy`  | An objective, a rationale, and an optional fictional KPI.                                      |
| `mission`   | A mission, vision, values, or purpose statement.                                               |
| `email`     | Subject, greeting, body, and a corporate close.                                                |
| `jargon`    | A sarcastic definition, a lookup, or the whole list.                                           |
| `translate` | Ordinary English rewritten as corporate language. Also reads stdin.                            |
| `bingo`     | A buzzword card. Sizes 3, 5, and 7. The centre cell is `FREE SPACE`.                           |
| `document`  | A strategy, report, proposal, business plan, executive summary, or transformation plan.        |

`--count` prints more than one result, from 1 to 100. `--paragraphs` sets
the email body length and the document length, from 1 to 40.

| Flag        | Meaning                                      |
| ----------- | -------------------------------------------- |
| `--level`   | Bullshit intensity, 1 to 3. Default 2.       |
| `--count`   | How many results to generate, 1 to 100.      |
| `--seed`    | Repeatable generation.                       |
| `--format`  | `text`, `json`, or `markdown`.               |
| `--output`  | Write the result to a file.                  |
| `--force`   | Overwrite an existing output file.           |
| `--verbose` | Diagnostics on stderr.                       |
| `--quiet`   | Hide warnings.                               |
| `--config`  | TOML configuration file.                     |
| `--version` | Print `corporate-bullshit x.y.z` and exit 0. |

## Examples

These are the exact lines those seeds print with the built-in vocabulary.

### Statements

```bash
corporate-bullshit generate --level 1 --seed 7
```

```text
We should align the goal so the team can support finished work.
```

```bash
corporate-bullshit generate --level 2 --seed 20
```

```text
Our customer-centric capability model will optimise predictable delivery.
```

```bash
corporate-bullshit generate --level 3 --seed 1
```

```text
We must gamify our bleeding-edge change programme to ideate synergised stakeholder bliss.
```

### Meetings

```bash
corporate-bullshit meeting --type avoidance --seed 26
```

```text
Let's circle back and leverage the innovation pipeline with clients before we answer.
```

Other `--type` values: `agreement`, `deflection`, `followup`, `strategy`,
`objection`, `summary`, and `random`.

### Excuses

```bash
corporate-bullshit excuse --topic deadline --seed 9
```

```text
Due to evolving cross-functional dependencies, we've had to track our delivery expectations to stay aligned with the delivery cadence.
```

Other `--topic` values: `budget`, `technical`, `meeting`, `report`,
`project`, `performance`, `communication`, and `random`.

### Strategy

```bash
corporate-bullshit strategy --seed 1
```

```text
Objective: Make the delivery cadence customer-centric enough that the leadership team can use it.
Rationale: This enables transformational progress across the strategic deliverables and gives the architecture forum a clearer path to clearer priorities.
KPI (fictional): Increase delivery predictability by 42%.
```

> **Note:** Every KPI, percentage, and financial figure is fictional.

`--no-kpi` drops the metric.

### Mission Statements

```bash
corporate-bullshit mission --company "Acme Corp" --seed 6
```

```text
The mission of Acme Corp is to strengthen an innovative value proposition so steady progress follows.
```

`--type` is `mission`, `vision`, `values`, `purpose`, or `random`.

### Emails

```bash
corporate-bullshit email --type followup --recipient "the team" --paragraphs 2 --seed 3
```

```text
Subject: Follow-up: next step on the strategic value stream

Dear the team,

I am following up so we can embed the cross-functional innovation pipeline with regional leads.

Following up on the plan. Could you strengthen it when you have a moment?

Kind regards,
```

Other `--type` values: `update`, `apology`, `announcement`, `request`,
`escalation`, `reminder`, and `random`. `--sender` adds a name under the close.

### Jargon

```bash
corporate-bullshit jargon --define synergy
```

```text
Synergy: The mysterious force that supposedly makes two inefficient departments collectively more productive.
```

```bash
corporate-bullshit jargon --count 3 --seed 4
```

```text
Operationalise: To turn a slogan into a programme, and the programme into more slogans.
Buy-in: Permission from people who were not going to do the work anyway.
Leverage: To use a thing, but with the implication that a fulcrum was involved.
```

Lookups ignore case and extra spaces. `--list` prints the terms.
An unknown term is an error.

### Translation

```bash
corporate-bullshit translate "We need to finish this today" --level 3
```

```text
We must strategically accelerate the completion of this deliverable within the current operational timeframe.
```

The translator is a fixed set of phrase and word rules. A line it does not
recognise is printed unchanged. With no argument, it reads standard input.

### Bingo

```bash
corporate-bullshit bingo --size 3 --seed 12345
```

```text
+---------------+------------+------------+
| headwind      | bandwidth  | pain point |
+---------------+------------+------------+
| cascade       | FREE SPACE | OKR        |
+---------------+------------+------------+
| best practice | workstream | unblock    |
+---------------+------------+------------+
```

The default size is 5. Terms are not repeated on a card. `--format markdown`
prints a table, and `--format json` prints the grid.

### Documents

```bash
corporate-bullshit document --type executive-summary --company "Acme Corp" --paragraphs 3 --seed 8
```

```text
Acme Corp: Executive Summary

Executive Summary

Progress depends on our ability to plan the goal without adding another layer of unread RACI charts.

Expected Outcomes

- The leadership team can plan measurable business impact.

Recommendations

- Ask the leadership team to optimise the operating model before adding more scope.
```

Other `--type` values: `strategy`, `report`, `proposal`, `business-plan`,
`transformation-plan`, and `random`. A document keeps a small set of terms
so the sections sound like the same piece of writing. Markdown output uses
headings. JSON output is one object per section.

## Output

`--format text` is the default and is safe to pipe. `--format json` is the
only thing written to stdout for that run:

```bash
corporate-bullshit generate --seed 20 --format json
```

```json
{
  "mode": "generate",
  "vocabulary_version": "1",
  "seed": 20,
  "level": 2,
  "count": 1,
  "results": [
    "Our customer-centric capability model will optimise predictable delivery."
  ]
}
```

The seed is included only when you passed `--seed`. `--format markdown`
uses headings, lists, and tables where they fit.

`--output report.md` writes the file and leaves an existing file alone
unless you also pass `--force`. Diagnostics and warnings go to stderr.
Colour is used for text labels when stdout is a terminal. `--no-colour`,
or `NO_COLOR`, turns it off.

## Configuration

The tool works with no configuration file. An optional TOML file can set
the defaults. Command-line options win.

```toml
level = 2
format = "text"
count = 1
paragraphs = 3
colour = true
company = "Acme Corp"
vocabulary = ["extra-words.toml"]
templates = ["extra-patterns.toml"]
```

Search order:

1. `--config`
2. `CORPORATE_BULLSHIT_CONFIG`
3. `./corporate-bullshit.toml`
4. `$XDG_CONFIG_HOME/corporate-bullshit/config.toml`, or `~/.config/corporate-bullshit/config.toml`

A missing default file is ignored. A missing file passed with `--config`
is an error. Extra vocabulary and templates are data only. Invalid entries
are skipped with a warning. They are never executed.

## Exit Codes

| Result                       | Exit |
| ---------------------------- | ---- |
| Success                      | 0    |
| Generation failed            | 1    |
| Invalid arguments or config  | 2    |
| Input or output file error   | 3    |
| Vocabulary or template error | 4    |

A closed output pipe is still success.

## Library

```python
from lupaxa.corporate_bullshit import generate, meeting, translate

generate(level=3, count=2, seed=12345)
meeting(kind="avoidance", seed=26)
translate("We need to finish this today", level=3)
```

The same functions back the commands: `generate`, `meeting`, `excuse`,
`strategy`, `mission`, `email`, `jargon_define`, `jargon_list`,
`jargon_random`, `translate`, `bingo`, and `document`. Pass `seed` when a
caller needs the same result twice.

## Development

```bash
make init
make python-install-dev
make python-check
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
