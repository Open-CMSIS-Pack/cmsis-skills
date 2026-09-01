# CMSIS Skills

CMSIS Skills collects resources for AI agents that help developers build embedded applications using CMSIS APIs, software components, and CMSIS Solution project-based tools for build, programming, debugging, and analysis.

The repository is organized into independent top-level collections so it can grow beyond skills without mixing their documentation, templates, and resources.

## Repository contents

| Collection | Description |
| --- | --- |
| [Generic MCU Skills](generic-mcu-skills/README.md) | Reusable AI-agent skills for MCU project creation, device bring-up, debug and trace, software packs, and DevOps. The skills are applicable across MCU families and are mostly toolchain- and RTOS-agnostic. |
| [Workspace agent skills](.agents/skills/) | Repository-local skills that help AI agents maintain this workspace and keep its skills, templates, and documentation consistent. |

## Workspace agent skills

The [`.agents/skills/`](.agents/skills/) directory contains contributor tooling specific to this repository. These skills maintain CMSIS Skills content; they are not reusable MCU workflow skills from the Generic MCU Skills collection.

- [`maintain-workspace-skills`](.agents/skills/maintain-workspace-skills/SKILL.md) applies the repository and collection guidance when a skill, skill resource, template, or skill catalog documentation is created or changed. It also verifies structure, companion metadata, README entries, and available validation results.

## How to use a skill

Choose a skill whose description matches the task, make it available to your AI agent using the agent product's supported installation or discovery mechanism, and ask the agent to use it by name. Provide the inputs listed in the skill's prerequisites, such as the project, device information, or required artifacts.

For example, with a CMSIS solution workspace open, ask:

```text
Use $create-csolution-github-action. Build all targets and use FVP
tests for targets that support them.
```

## How to create skills

Use a two-step approach:

1. Work with an AI agent to complete the task once and create a reviewed artifact.
2. Ask the AI agent to turn that pre-work into a skill. Point to the work in step 1, the destination for the skill, and the skill-maintenance guidance.

For example, after completing and reviewing the DevOps workflow under topic A, use a prompt such as:

```text
Create a skill for generating GitHub Actions workflows for DevOps in
cmsis-skills\generic-mcu-skills\skills\devops. Follow the workspace
guidance in
cmsis-skills\.agents\skills\maintain-workspace-skills\SKILL.md.

Use the knowledge and validated artifact from the pre-work under topic A.
Create two reusable GitHub Actions templates: one for a single target and one
using a target matrix.

Start with the currently loaded solution discovered through
.vscode\cmsis.json. This file also identifies the selected target to pass to
the --active option.

If the solution has multiple target-types, ask whether to check only the
active target or all targets. Use a matrix when all targets are selected.

If a target's debugger name starts with FVP, offer to add a test on the FVP
simulation model. Add a stub that checks whether the FVP produced output,
because the application's expected output is not yet known. Offer to run an
existing test and use confirmed output to replace the stub with a meaningful
check.

Do not start an FVP for targets whose debugger name does not start with FVP.
Represent these targets with an empty matrix variable.

Limit the workflow permissions to read-only repository contents.

Use these workflow filenames:

- build-<solution-name>.yml when no FVP test is included
- test-<solution-name>.yml when an FVP test is included
```

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution process and the README of a collection for its content-specific guidance.

## Related projects

The [Arm Examples](https://github.com/Arm-Examples) organization provides embedded example projects that may be used as realistic inputs and validation targets for resources in this repository.
