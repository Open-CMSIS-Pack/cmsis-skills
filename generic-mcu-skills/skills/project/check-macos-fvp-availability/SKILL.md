---
name: check-macos-fvp-availability
description: Check whether a selected CMSIS solution target needs an Arm FVP on macOS, and offer setup through FVPs-on-Mac when its model is unavailable.
---

# Check macOS FVP Availability

## Target & Persona

- **Role:** Environment verification engineer
- **Objective:** Determine whether the selected CMSIS solution target can find its required FVP on this macOS host, and offer the upstream container setup when needed.

## Prerequisites & Context

- **Expected input:** The workspace, selected `*.csolution.yml`, and target type. Use reliable active-solution state, such as `.vscode/cmsis.json`, when the user has not specified them.
- **Dependencies:** macOS only for the setup offer; [Arm-Examples/FVPs-on-Mac](https://github.com/Arm-Examples/FVPs-on-Mac) and Git for the optional setup; either Docker Desktop or Apple Container as the running container runtime; an applicable Arm user-based license for use of its FVPs. Apple Container requires Apple silicon and macOS 26 or later; Docker Desktop supports Intel and Apple silicon Macs.
- **Portability:** The check applies to any CMSIS solution target. The offered setup is macOS-specific and covers only models available in the upstream Arm Virtual Hardware FVP package; it assumes no MCU family, compiler, RTOS, or probe.

## Execution Steps (Strict Workflow)

1. **Analysis:** Identify the actual host with `uname -s`. Resolve the explicitly requested solution and target, or use reliable active-solution state. If either remains ambiguous, ask for that selection. Parse the solution as YAML and inspect the selected target type's `target-set` debugger definition and any model path or command it references. A target needs an FVP only when the selected execution configuration names an FVP model (for example, `debugger.model: FVP_...`); a pack requirement or an FVP target elsewhere in the solution alone is insufficient.
2. **Processing:** On non-macOS hosts or targets without an FVP requirement, report the finding and stop. On macOS, check whether the exact required model is already available through the configured path or `PATH`, and whether its `--version` command succeeds. If the model is present but the command fails, report the failure and its likely prerequisite; do not offer a duplicate installation. If it is absent, explain that [FVPs-on-Mac](https://github.com/Arm-Examples/FVPs-on-Mac) runs Linux FVPs through Docker Desktop or Apple Container, name the required model, and offer setup in a user-chosen location with a supported runtime. If both runtimes are installed and no choice has been saved, ask which one to use. Verify that the upstream package contains the model before claiming the setup can satisfy the target; if coverage cannot be established in advance, state that it remains unverified.
3. **Validation:** If the user accepts the setup offer, follow the current [upstream README](https://github.com/Arm-Examples/FVPs-on-Mac/blob/main/README.md). Check the selected runtime: `docker info` for Docker Desktop; `uname -m` and the macOS version for Apple Container eligibility, then `container system status` after starting its service if needed. Clone the repository into the agreed location and run its `./build.sh` using the selected runtime. When both CLIs are present, use the user's choice through the upstream `FVP_RUNTIME=docker|container` setting so setup saves it in `.fvp-runtime`. Inspect the generated `bin` wrappers. Verify that the exact required wrapper exists and that `<checkout>/bin/<model> --version` succeeds using the selected runtime. The runtimes keep separate images, so do not treat an image built in one as available in the other. The wrapper must be reachable from the development environment that launches the model; add its `bin` directory to that environment's `PATH` only with the user's chosen persistence scope. Recheck model discovery from that environment. Report separately if the model needs a license, mount configuration, or project-specific run/debug integration before it can execute the solution.
4. **Formatting:** Report host OS, selected solution and target, the model requirement and source field, current model availability, selected runtime when applicable, and either the installation offer or the setup and validation result.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not infer an FVP requirement from a target name, device, pack, or another target's debugger. Do not assume the upstream image contains every FVP model.
- **Portability:** Keep macOS-specific setup out of other host workflows. Do not change compiler, RTOS, board, or debug settings as part of this check.
- **Critical blockers:** Stop setup when the selected solution or target is ambiguous, neither supported runtime is available, the selected runtime cannot start, the checkout cannot be obtained, the build fails, or the required wrapper is absent. Report the observed state and next action.
- **Scope:** Do not clone, build an image, edit shell startup files, or modify solution/debug configuration merely to perform the check. Offer setup first; carry it out only after the user accepts the concrete installation location and steps. Do not run or debug the target as an availability test.
- **Tone and style:** Respond factually and directly.

## Expected Output

A concise availability report and, only when macOS needs a missing FVP, a concrete FVPs-on-Mac setup offer with a supported runtime. After accepted setup, report the runtime, checkout path, required wrapper path, version-check result, and any remaining integration requirement. No project artifact is created by the check.

## Validation Resources

- [FVPs-on-Mac README](https://github.com/Arm-Examples/FVPs-on-Mac/blob/main/README.md): current Docker Desktop and Apple Container prerequisites, runtime selection, build, wrapper, license, and mount instructions.
- The selected `*.csolution.yml` and active-solution state: repeat the same target resolution and model lookup after setup.
