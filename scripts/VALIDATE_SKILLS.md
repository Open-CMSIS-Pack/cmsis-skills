# Skill Catalog Validator

`scripts/validate_skills.py` checks the structure and references of the skill catalog. It is used by the
`Validate Skills` GitHub Actions workflow and can also be run locally.

## Run locally

From the repository root:

```text
python -m pip install pyyaml
python scripts/validate_skills.py --verbose
```

On Windows, `py` can be used instead of `python`:

```text
py scripts/validate_skills.py
```

The command exits with status `0` when all checks pass and status `1` when one or more validation errors are
found. It exits with status `2` when PyYAML is not installed.

The default output is concise. Use `--verbose` when per-skill progress is useful:

```text
py scripts/validate_skills.py --verbose
```

Use `--quiet` to suppress the start message and report only issues and the final result:

```text
py scripts/validate_skills.py --quiet
```

## Checks performed

For every `SKILL.md` under `generic-mcu-skills/skills/`, the validator checks:

- At least one skill file exists.
- YAML frontmatter exists and is valid.
- Frontmatter contains non-empty `name` and `description` values.
- The frontmatter `name` matches the skill directory name.
- Skill names are unique.
- Required operational sections are present:
  - workflow or execution steps;
  - output or expected output;
  - resources or generated-project validation.
- Relative Markdown links point to existing files inside the repository.

When a skill contains `agents/openai.yaml`, the validator also checks:

- The file is valid YAML.
- An `interface` mapping exists.
- `display_name`, `short_description`, and `default_prompt` are non-empty.

## Output

The validator reports the total workload, progress for each skill, and a final result. Paths use `/` on every
platform so logs are easy to scan and compare:

```text
INFO: Validating 5 skill files under generic-mcu-skills/skills
INFO: Checking 1/5: generic-mcu-skills/skills/project/check-cmsis-environment/SKILL.md
...
INFO: Validation passed: checked 5 skill(s); metadata, required sections, local links, and agent YAML are valid.
```

Failures are logged at `ERROR` level and include the affected file and a specific reason, for example:

```text
ERROR: Validation failed with 1 issue(s):
ERROR:   generic-mcu-skills/skills/project/check-cmsis-environment/SKILL.md: broken local link: missing-reference.md
ERROR: Checked 5 skill(s); review the issues above.
```

## What it does not check

This is a static catalog check. It does not execute the skills or verify:

- CMSIS-Toolbox, `cbuild`, CMake, Ninja, or compiler installation;
- Zephyr, Python virtual environments, or `west`;
- CMSIS board, device, or pack identifiers;
- generated-project setup or compilation;
- external URLs;
- agent response quality or compliance with the skill instructions.

Those checks require separate integration tests with pinned CMSIS and Zephyr environments.
