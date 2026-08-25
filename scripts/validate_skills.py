"""Validate the structure and references of the skill catalog."""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:
    print("PyYAML is required: python -m pip install pyyaml", file=sys.stderr)
    raise SystemExit(2)


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "generic-mcu-skills" / "skills"
REQUIRED_SECTION_GROUPS = (
    ("Execution Steps (Strict Workflow)", "Workflow"),
    ("Expected Output", "Output"),
    ("Validation Resources", "Resources", "Validate the Generated Project"),
)
FRONTMATTER_PATTERN = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
LOGGER = logging.getLogger("validate_skills")


HEADING_PATTERN = re.compile(r"^## (.+?)\s*$", re.MULTILINE)
LINK_PATTERN = re.compile(r"!?\[[^]]*\]\(([^)]+)\)")


def display_path(path: Path) -> str:
    """Return a stable, readable repository-relative path."""
    return path.relative_to(ROOT).as_posix()


def error(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{display_path(path)}: {message}")


def validate_frontmatter(path: Path, text: str, errors: list[str]) -> dict:
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        error(errors, path, "missing YAML frontmatter")
        return {}

    try:
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        error(errors, path, f"invalid YAML frontmatter: {exc}")
        return {}

    if not isinstance(metadata, dict):
        error(errors, path, "frontmatter must be a YAML mapping")
        return {}
    for key in ("name", "description"):
        if not isinstance(metadata.get(key), str) or not metadata[key].strip():
            error(errors, path, f"frontmatter requires a non-empty {key!r}")
    return metadata


def validate_links(path: Path, text: str, errors: list[str]) -> None:
    for target in LINK_PATTERN.findall(text):
        target = target.strip().split()[0]
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or target.startswith("#"):
            continue

        local_target = unquote(parsed.path)
        candidate = (path.parent / local_target).resolve()
        try:
            candidate.relative_to(ROOT)
        except ValueError:
            error(errors, path, f"link escapes repository: {target}")
            continue
        if not candidate.exists():
            error(errors, path, f"broken local link: {target}")


def validate_skill(path: Path, errors: list[str], names: dict[str, Path]) -> None:
    text = path.read_text(encoding="utf-8")
    metadata = validate_frontmatter(path, text, errors)
    name = metadata.get("name")
    skill_dir = path.parent.name

    if isinstance(name, str):
        if name != skill_dir:
            error(errors, path, f"frontmatter name {name!r} does not match directory {skill_dir!r}")
        if name in names:
            error(errors, path, f"duplicate skill name also used by {names[name].relative_to(ROOT)}")
        names[name] = path

    headings = set(HEADING_PATTERN.findall(text))
    for section_group in REQUIRED_SECTION_GROUPS:
        if not headings.intersection(section_group):
            error(errors, path, f"missing required section: one of {section_group}")

    validate_links(path, text, errors)

    agent_path = path.parent / "agents" / "openai.yaml"
    if agent_path.exists():
        try:
            agent = yaml.safe_load(agent_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            error(errors, agent_path, f"invalid YAML: {exc}")
            return
        interface = agent.get("interface") if isinstance(agent, dict) else None
        if not isinstance(interface, dict):
            error(errors, agent_path, "requires an interface mapping")
            return
        for key in ("display_name", "short_description", "default_prompt"):
            if not isinstance(interface.get(key), str) or not interface[key].strip():
                error(errors, agent_path, f"interface requires a non-empty {key!r}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="only report validation issues and the final result",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="report each skill as it is checked",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        force=True,
    )
    errors: list[str] = []
    skill_files = sorted(SKILLS_ROOT.glob("**/SKILL.md"))
    if not skill_files:
        LOGGER.error("No skills found under %s", SKILLS_ROOT)
        return 1

    if not args.quiet:
        LOGGER.info("Validating %d skill files under %s", len(skill_files), display_path(SKILLS_ROOT))
    names: dict[str, Path] = {}
    for index, path in enumerate(skill_files, start=1):
        if args.verbose and not args.quiet:
            LOGGER.info("Checking %d/%d: %s", index, len(skill_files), display_path(path))
        validate_skill(path, errors, names)

    if errors:
        LOGGER.error("Validation failed with %d issue(s):", len(errors))
        for item in errors:
            LOGGER.error("  %s", item)
        LOGGER.error("Checked %d skill(s); review the issues above.", len(skill_files))
        return 1

    LOGGER.info(
        "Validation passed: checked %d skill(s); metadata, required sections, local links, "
        "and agent YAML are valid.",
        len(skill_files),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())