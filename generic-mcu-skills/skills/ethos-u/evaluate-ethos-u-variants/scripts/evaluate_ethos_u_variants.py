#!/usr/bin/env python3
"""Compare Vela estimates for a quantized model across Ethos-U candidates."""

from __future__ import annotations

import argparse
import csv
import re
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence


DEFAULT_CANDIDATES = (
    ("ethos-u55-128", "Ethos_U55_Deep_Embedded", "Shared_Sram"),
    ("ethos-u85-256", "Ethos_U85_SYS_DRAM_High", "Shared_Sram"),
)
OPTIMISATIONS = ("Size", "Performance")
SUMMARY_FIELDS = (
    "sram_memory_used",
    "dram_memory_used",
    "on_chip_flash_memory_used",
    "off_chip_flash_memory_used",
    "inference_time",
)


class EvaluationError(RuntimeError):
    """A fatal error that must stop the complete comparison."""


@dataclass(frozen=True)
class Candidate:
    accelerator: str
    system_config: str
    memory_mode: str


@dataclass(frozen=True)
class Result:
    optimisation: str
    candidate: Candidate
    reported_accelerator: str
    sram_kib: float
    dram_kib: float
    on_chip_flash_kib: float
    off_chip_flash_kib: float
    inference_time_ms: float
    cpu_operators: int | None
    npu_operators: int | None
    build_dir: Path

    @property
    def other_memory_kib(self) -> float:
        return self.dram_kib + self.on_chip_flash_kib + self.off_chip_flash_kib


def positive_seconds(value: str) -> float:
    try:
        seconds = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number") from exc
    if seconds <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return seconds


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare Vela memory and estimated performance for a quantized "
            "TFLite or TOSA model across Ethos-U configurations."
        )
    )
    parser.add_argument("model", type=Path, help="existing .tflite or .tosa model")
    parser.add_argument(
        "--candidate",
        action="append",
        nargs=3,
        metavar=("ACCELERATOR", "SYSTEM_CONFIG", "MEMORY_MODE"),
        help="replace the defaults; repeat for every candidate",
    )
    parser.add_argument(
        "--vela-config",
        "--config",
        dest="vela_config",
        default="Arm/vela.ini",
        help=(
            "device-specific .ini path or installed Vela config name "
            "(default: the installed Arm/vela.ini)"
        ),
    )
    parser.add_argument(
        "--timeout-seconds",
        type=positive_seconds,
        default=300.0,
        help="shared deadline for all model compilations (default: 300)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help=(
            "empty comparison directory (default: .agent-artifacts/"
            "ethos-u-evaluation/<model>-<UTC timestamp>)"
        ),
    )
    return parser.parse_args(argv)


def command_text(command: Sequence[str]) -> str:
    return shlex.join(str(part) for part in command)


def run_checked(
    command: Sequence[str], stage: str, timeout: float, log_path: Path | None = None
) -> subprocess.CompletedProcess[str]:
    try:
        completed = subprocess.run(
            [str(part) for part in command],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        write_log(log_path, command, stdout, stderr)
        detail = f"; log: {log_path}" if log_path else ""
        raise EvaluationError(
            f"{stage} exceeded the remaining {timeout:.1f} second deadline{detail}"
        ) from exc
    except OSError as exc:
        raise EvaluationError(f"could not run {stage}: {exc}") from exc

    write_log(log_path, command, completed.stdout, completed.stderr)
    if completed.returncode != 0:
        detail = f"\nLog: {log_path}" if log_path else ""
        output = (completed.stderr or completed.stdout).strip()
        if output:
            output = f"\n{output}"
        raise EvaluationError(
            f"{stage} failed with exit code {completed.returncode}: "
            f"{command_text(command)}{detail}{output}"
        )
    return completed


def write_log(
    log_path: Path | None, command: Sequence[str], stdout: str, stderr: str
) -> None:
    if log_path is None:
        return
    sections = [f"Command: {command_text(command)}\n", "\n--- stdout ---\n", stdout]
    if stderr:
        sections.extend(("\n--- stderr ---\n", stderr))
    log_path.write_text("".join(sections), encoding="utf-8")


def validate_model(model: Path) -> Path:
    resolved = model.expanduser().resolve()
    if not resolved.exists():
        raise EvaluationError(f"model does not exist: {resolved}")
    if not resolved.is_file():
        raise EvaluationError(f"model path is not a file: {resolved}")
    if resolved.suffix.lower() not in {".tflite", ".tosa"}:
        raise EvaluationError("model must use the .tflite or .tosa extension")
    try:
        with resolved.open("rb") as stream:
            header = stream.read(256)
    except OSError as exc:
        raise EvaluationError(f"model cannot be read: {resolved}: {exc}") from exc
    if header.startswith(b"version https://git-lfs.github.com/spec/v1"):
        size_match = re.search(rb"^size (\d+)$", header, re.MULTILINE)
        expected = (
            f" for a {int(size_match.group(1))}-byte object" if size_match else ""
        )
        raise EvaluationError(
            f"model content is unavailable: {resolved} is a Git LFS pointer{expected}; "
            "retrieve the model outside this skill"
        )
    return resolved


def default_output_dir(model: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", model.stem).strip("-_") or "model"
    return (
        Path.cwd()
        / ".agent-artifacts"
        / "ethos-u-evaluation"
        / f"{name}-{stamp}"
    )


def prepare_output_dir(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if resolved.exists():
        if not resolved.is_dir():
            raise EvaluationError(f"output path is not a directory: {resolved}")
        if any(resolved.iterdir()):
            raise EvaluationError(f"output directory is not empty: {resolved}")
    else:
        resolved.mkdir(parents=True)
    return resolved


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-_").lower()


def parse_operator_count(output: str, kind: str) -> int | None:
    match = re.search(rf"^{kind} operators\s*=\s*(\d+)", output, re.MULTILINE)
    return int(match.group(1)) if match else None


def read_summary(
    build_dir: Path, candidate: Candidate, optimisation: str, output: str
) -> Result:
    summaries = list(build_dir.glob("*_summary_*.csv"))
    if len(summaries) != 1:
        raise EvaluationError(
            f"expected one Vela summary CSV in {build_dir}, found {len(summaries)}"
        )
    with summaries[0].open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 1:
        raise EvaluationError(
            f"expected one data row in Vela summary CSV {summaries[0]}, "
            f"found {len(rows)}"
        )
    row = rows[0]
    missing = [field for field in SUMMARY_FIELDS if not row.get(field)]
    if missing:
        raise EvaluationError(
            f"Vela summary CSV {summaries[0]} is missing values: {', '.join(missing)}"
        )
    try:
        return Result(
            optimisation=optimisation,
            candidate=candidate,
            reported_accelerator=row.get("accelerator_configuration", ""),
            sram_kib=float(row["sram_memory_used"]),
            dram_kib=float(row["dram_memory_used"]),
            on_chip_flash_kib=float(row["on_chip_flash_memory_used"]),
            off_chip_flash_kib=float(row["off_chip_flash_memory_used"]),
            inference_time_ms=float(row["inference_time"]) * 1000.0,
            cpu_operators=parse_operator_count(output, "CPU"),
            npu_operators=parse_operator_count(output, "NPU"),
            build_dir=build_dir,
        )
    except ValueError as exc:
        raise EvaluationError(
            f"Vela summary CSV {summaries[0]} contains a non-numeric result"
        ) from exc


def operator_text(result: Result) -> str:
    if result.cpu_operators is None or result.npu_operators is None:
        return "unavailable"
    return f"{result.cpu_operators}/{result.npu_operators}"


def write_csv_report(path: Path, results: Sequence[Result]) -> None:
    fieldnames = (
        "optimisation",
        "accelerator_configuration",
        "reported_accelerator_configuration",
        "system_config",
        "memory_mode",
        "sram_memory_kib",
        "dram_memory_kib",
        "on_chip_flash_memory_kib",
        "off_chip_flash_memory_kib",
        "other_memory_kib",
        "estimated_inference_time_ms",
        "cpu_operators",
        "npu_operators",
        "build_directory",
    )
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "optimisation": result.optimisation,
                    "accelerator_configuration": result.candidate.accelerator,
                    "reported_accelerator_configuration": result.reported_accelerator,
                    "system_config": result.candidate.system_config,
                    "memory_mode": result.candidate.memory_mode,
                    "sram_memory_kib": f"{result.sram_kib:.6f}",
                    "dram_memory_kib": f"{result.dram_kib:.6f}",
                    "on_chip_flash_memory_kib": f"{result.on_chip_flash_kib:.6f}",
                    "off_chip_flash_memory_kib": f"{result.off_chip_flash_kib:.6f}",
                    "other_memory_kib": f"{result.other_memory_kib:.6f}",
                    "estimated_inference_time_ms": f"{result.inference_time_ms:.6f}",
                    "cpu_operators": result.cpu_operators,
                    "npu_operators": result.npu_operators,
                    "build_directory": str(result.build_dir),
                }
            )


def operation_warning(results: Sequence[Result]) -> str | None:
    counts = {(item.cpu_operators, item.npu_operators) for item in results}
    if any(None in count for count in counts):
        return "CPU/NPU operator counts could not be read from every Vela report."
    if len(counts) != 1:
        return "CPU/NPU operator counts differ between builds; compare estimates with care."
    return None


def write_markdown_report(
    path: Path,
    model: Path,
    vela_path: str,
    vela_version: str,
    config: str,
    timeout_seconds: float,
    results: Sequence[Result],
) -> str | None:
    warning = operation_warning(results)
    lines = [
        "# Ethos-U configuration comparison",
        "",
        f"- Model: `{model}`",
        f"- Vela: `{vela_path}` ({vela_version})",
        f"- Configuration file: `{config}`",
        f"- Shared compilation limit: {timeout_seconds:g} seconds",
        "",
        "> [!CAUTION]",
        "> Vela cycle counts and inference times are estimates. Validate the selected",
        "> configuration on target hardware.",
        "",
        "`Other memory` is the sum of Vela's DRAM, on-chip Flash, and off-chip",
        "Flash memory totals. See `comparison.csv` for the separate values.",
    ]
    if warning:
        lines.extend(("", "> [!WARNING]", f"> {warning}"))

    headings = {
        "Size": "Optimize for memory size",
        "Performance": "Optimize for performance",
    }
    for optimisation in OPTIMISATIONS:
        lines.extend(
            (
                "",
                f"## {headings[optimisation]}",
                "",
                "| Accelerator | System configuration | Memory mode | SRAM | Other memory | Estimated time | CPU/NPU operators |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: |",
            )
        )
        for result in (r for r in results if r.optimisation == optimisation):
            lines.append(
                f"| `{result.candidate.accelerator}` | "
                f"`{result.candidate.system_config}` | "
                f"`{result.candidate.memory_mode}` | "
                f"{result.sram_kib:.2f} KiB | "
                f"{result.other_memory_kib:.2f} KiB | "
                f"{result.inference_time_ms:.3f} ms | "
                f"{operator_text(result)} |"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return warning


def evaluate(args: argparse.Namespace) -> int:
    model = validate_model(args.model)
    vela_path = shutil.which("vela")
    if vela_path is None:
        raise EvaluationError("vela is not installed or is not available on PATH")

    version_result = run_checked([vela_path, "--version"], "Vela version check", 15.0)
    vela_version = version_result.stdout.strip() or version_result.stderr.strip()
    if not vela_version:
        raise EvaluationError("vela --version returned no version")
    print(f"Vela executable: {vela_path}")
    print(f"Vela version: {vela_version}")

    run_checked(
        [vela_path, "--list-configs", args.vela_config],
        f"Vela configuration check for {args.vela_config}",
        30.0,
    )

    candidates = [Candidate(*values) for values in (args.candidate or DEFAULT_CANDIDATES)]
    output_dir = prepare_output_dir(args.output_dir or default_output_dir(model))
    output_format = "raw" if model.suffix.lower() == ".tosa" else "tflite"
    results: list[Result] = []
    deadline = time.monotonic() + args.timeout_seconds

    for candidate_index, candidate in enumerate(candidates, start=1):
        candidate_dir = (
            f"{candidate_index:02d}-{slug(candidate.accelerator)}-"
            f"{slug(candidate.system_config)}-{slug(candidate.memory_mode)}"
        )
        for optimisation in OPTIMISATIONS:
            build_dir = output_dir / candidate_dir / optimisation.lower()
            build_dir.mkdir(parents=True)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise EvaluationError(
                    f"shared {args.timeout_seconds:g} second compilation deadline expired "
                    f"before {candidate.accelerator} {optimisation}"
                )
            command = [
                vela_path,
                str(model),
                "--accelerator-config",
                candidate.accelerator,
                "--config",
                args.vela_config,
                "--system-config",
                candidate.system_config,
                "--memory-mode",
                candidate.memory_mode,
                "--optimise",
                optimisation,
                "--output-format",
                output_format,
                "--output-dir",
                str(build_dir),
                "--verbose-cycle-estimate",
            ]
            stage = (
                f"Vela compile for {candidate.accelerator}, "
                f"{candidate.system_config}, {candidate.memory_mode}, {optimisation}"
            )
            print(f"Compiling: {stage}")
            completed = run_checked(
                command, stage, remaining, build_dir / "vela.log"
            )
            results.append(
                read_summary(build_dir, candidate, optimisation, completed.stdout)
            )

    csv_path = output_dir / "comparison.csv"
    markdown_path = output_dir / "comparison.md"
    write_csv_report(csv_path, results)
    warning = write_markdown_report(
        markdown_path,
        model,
        vela_path,
        vela_version,
        args.vela_config,
        args.timeout_seconds,
        results,
    )

    print("Status: PASS")
    print(f"Markdown report: {markdown_path}")
    print(f"CSV report: {csv_path}")
    if warning:
        print(f"Warning: {warning}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    try:
        return evaluate(parse_args(argv if argv is not None else sys.argv[1:]))
    except EvaluationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print("Status: FAIL", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
