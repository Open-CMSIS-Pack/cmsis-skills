---
name: evaluate-ethos-u-variants
description: Evaluate an existing pre-trained, quantized TFLite or TOSA model across Arm Ethos-U Vela configurations, comparing memory use and estimated performance without installing tools or models. Use when selecting an Ethos-U accelerator, MAC configuration, reference system, memory mode, or optimization strategy.
---

# Evaluate Ethos-U Variants

## Target & Persona

- **Role:** ML integration and performance engineer
- **Objective:** Compare Vela memory requirements and estimated inference time for the same quantized ML model across candidate Ethos-U configurations.

## Prerequisites & Context

- **Required input:** A user-provided path to an existing pre-trained, quantized `.tflite` or `.tosa` model. Ask for this path when it is absent; do not select or download a model.
- **Optional input:** A path to a device-specific `vela.ini` file and matching candidate accelerator, system, and memory configurations.
- **Dependencies:** An already installed `vela` command and Python 3. By default, use the generic `Arm/vela.ini` file supplied with that Vela installation.
- **Portability:** The runner supports Windows, macOS, and Linux host systems. The default `Arm/vela.ini` systems are generic reference configurations for evaluation, not descriptions of a production device.

## Execution Steps (Strict Workflow)

1. **Analysis:** Obtain the model path and any user overrides. Use the installed Vela compiler's `Arm/vela.ini`, the default candidates, and the five-minute compilation limit unless the user supplies replacements. When the user selects a device-specific configuration file, obtain candidate triples that exist in that file.
2. **Processing:** Run `scripts/evaluate_ethos_u_variants.py`. The script verifies that the model contains data and is not a Git LFS pointer, then checks the Vela command, Vela version, and configuration file before compiling each candidate for both size and performance.
3. **Validation:** Require every Vela invocation to succeed within one shared compilation deadline. Confirm that each build produces a Vela summary CSV; stop the complete process on the first failure.
4. **Formatting:** Report the installed Vela version and the generated Markdown and CSV paths. Summarize the two comparison tables and any operator-placement warning.

### Default comparison

With no overrides, compare these candidates from `Arm/vela.ini`:

| Accelerator | System configuration | Memory mode |
| --- | --- | --- |
| `ethos-u55-128` | `Ethos_U55_Deep_Embedded` | `Shared_Sram` |
| `ethos-u85-256` | `Ethos_U85_SYS_DRAM_High` | `Shared_Sram` |

Each candidate is compiled with `--optimise Size` and
`--optimise Performance`. The five-minute default applies to the combined time
of all Vela model compilations, not to each invocation.

Run the default comparison:

```console
python <skill-dir>/scripts/evaluate_ethos_u_variants.py <model.tflite-or-tosa>
```

Replace the comparison candidates by repeating `--candidate` with one complete
accelerator, system, and memory configuration triple:

```console
python <skill-dir>/scripts/evaluate_ethos_u_variants.py <model> \
  --candidate ethos-u55-256 Ethos_U55_High_End_Embedded Shared_Sram \
  --candidate ethos-u85-512 Ethos_U85_SYS_DRAM_Mid Shared_Sram
```

Use `--vela-config <path-to-vela.ini>` to select a device-specific file. Replace
the default candidates with `--candidate` values defined by that file. The
legacy `--config` spelling remains an alias for `--vela-config`.

```console
python <skill-dir>/scripts/evaluate_ethos_u_variants.py <model> \
  --vela-config <device-specific-vela.ini> \
  --candidate <accelerator> <system-configuration> <memory-mode>
```

Use `--timeout-seconds <seconds>` to replace the shared 300-second compilation
limit and `--output-dir <directory>` to select an empty output directory. Run
the script with `--help` for the complete command interface.

The script selects raw output for `.tosa` input and TFLite output for `.tflite`
input. This does not alter the reported comparison metrics.

## Guardrails & Constraints (Strict Rules)

- **No installation or acquisition:** Do not install, update, or repair Vela, Python, models, or configuration files. Do not access the network.
- **Critical blockers:** Return `FAIL` and stop when the model is missing, unreadable, represented only by a Git LFS pointer, or has another extension; when `vela` is unavailable or cannot report its version; when the selected configuration cannot be read; when the shared deadline expires; when a Vela compile fails; or when a summary CSV is absent or incomplete.
- **Fail fast:** Do not continue with remaining candidates or optimization settings after a fatal error. Preserve the failed build's `vela.log` when an output directory has already been created.
- **Configuration source:** Use `Arm/vela.ini` from the active Vela installation by default. Do not silently substitute a workspace or device-specific file. Use a device-specific file only when the user provides it.
- **Comparable inputs:** Use the same model, Vela version, Vela configuration file, and compiler options for all candidates except accelerator, system configuration, memory mode, and optimization setting.
- **Estimates:** Treat Vela cycle counts and inference times as estimates. Use them to compare candidates, then validate the selected configuration on target hardware.
- **No fabrication:** Report only values read from Vela's generated summary CSV and console output. Do not infer successful NPU placement or missing measurements.
- **Output safety:** Use a separate build directory for every candidate and optimization setting. Do not overwrite a non-empty user-selected output directory.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

On success, return `PASS` with:

- the resolved model path, Vela executable, and installed Vela version;
- the selected configuration file or installed `Arm/vela.ini` identifier and shared compilation limit;
- `.agent-artifacts/ethos-u-evaluation/<model>-<timestamp>/comparison.md`, unless the user selected another output directory;
- `comparison.csv`, retaining separate SRAM, DRAM, on-chip Flash, and off-chip Flash values from Vela;
- separate size and performance tables containing accelerator, system configuration, memory mode, SRAM, combined other memory, estimated inference time, and CPU/NPU operator counts;
- a warning when CPU/NPU operator counts differ between builds or cannot be read.

On failure, return `FAIL`, the failed stage or Vela command, the error output, and
the failed build log path when available. Do not present partial builds as a
comparison.

## Validation Resources

- Run `python <skill-dir>/scripts/evaluate_ethos_u_variants.py --help` to verify the runner interface.
- Run the script with a representative quantized model and confirm four default build directories, `comparison.md`, and `comparison.csv` are produced.
- Run it with a nonexistent model and confirm it reports `ERROR` and exits before invoking Vela.
- Run it with a Git LFS pointer and confirm it reports missing model content and exits before invoking Vela.
- Use `vela --list-configs Arm/vela.ini` only as a read-only check of the installed generic reference configurations.
