"""Validate Animita specs against spec/animita.schema.json.

Usage:
    python spec/validate.py spec/examples/*.json
    python spec/validate.py path/to/one_spec.json

Importable too:
    from validate import validate_spec
    ok, errors = validate_spec(spec_dict)
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).with_name("animita.schema.json")
_validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))


def _semantic_errors(spec):
    """Checks JSON Schema cannot express: unique ids, timing inside scenes, children rules."""
    errors = []
    for scene in spec.get("scenes", []):
        seen = set()
        sdur = scene.get("duration", 0)

        def walk(elements, path):
            for el in elements:
                eid = el.get("id")
                if eid in seen:
                    errors.append(f"{path}: duplicate element id '{eid}' in scene '{scene.get('id')}'")
                seen.add(eid)
                for a in el.get("animations", []):
                    if a["start"] >= sdur:
                        errors.append(f"{path}/{eid}: animation '{a['preset']}' starts at {a['start']}s, "
                                      f"after scene ends ({sdur}s)")
                    if a["preset"] == "stagger_children" and not el.get("children"):
                        errors.append(f"{path}/{eid}: stagger_children needs children")
                    if a["preset"] == "typewriter" and not el.get("content"):
                        errors.append(f"{path}/{eid}: typewriter needs content")
                    if a["preset"] == "counter_up" and el["type"] != "counter":
                        errors.append(f"{path}/{eid}: counter_up only works on type 'counter'")
                    if a["preset"] == "bar_grow" and el["type"] not in ("bar_chart", "progress_bar"):
                        errors.append(f"{path}/{eid}: bar_grow only works on bar_chart or progress_bar")
                if el.get("children") and el["type"] not in ("shape", "card", "device_frame"):
                    errors.append(f"{path}/{eid}: only shape, card and device_frame may have children")
                walk(el.get("children", []), f"{path}/{eid}")

        walk(scene.get("elements", []), scene.get("id", "?"))
    return errors


def validate_spec(spec):
    """Return (ok, errors). `errors` is a list of readable strings."""
    errors = []
    for e in sorted(_validator.iter_errors(spec), key=lambda e: list(e.absolute_path)):
        loc = "/".join(str(p) for p in e.absolute_path) or "(root)"
        errors.append(f"{loc}: {e.message[:200]}")
    if not errors:
        errors.extend(_semantic_errors(spec))
    return (not errors), errors


def main(paths):
    if not paths:
        print(__doc__)
        return 2
    failed = 0
    for p in paths:
        try:
            spec = json.loads(Path(p).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"FAIL  {p}\n   not readable JSON: {exc}")
            failed += 1
            continue
        ok, errs = validate_spec(spec)
        print(("OK    " if ok else "FAIL  ") + p)
        for e in errs:
            print("   " + e)
        failed += 0 if ok else 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
