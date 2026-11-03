from datetime import datetime, timezone, timedelta
from pathlib import Path
import sys

try:
    from zoneinfo import ZoneInfo
    IST = ZoneInfo("Asia/Kolkata")
except Exception:
    IST = timezone(timedelta(hours=5, minutes=30))

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

TODAY = datetime.now(IST).date().isoformat()


def inventory_report():
    ignored = {".git", "__pycache__", ".venv", "reports"}

    files = [
        path for path in ROOT.rglob("*")
        if path.is_file()
        and not any(part in ignored for part in path.parts)
    ]

    extension_counts = {}
    for path in files:
        extension = path.suffix.lower() or "no extension"
        extension_counts[extension] = extension_counts.get(extension, 0) + 1

    lines = [
        f"# Repository Inventory - {TODAY}",
        "",
        f"- Total project files: {len(files)}",
        "",
        "## File types",
        "",
    ]

    for extension, count in sorted(extension_counts.items()):
        lines.append(f"- {extension}: {count}")

    output = REPORTS / f"inventory-{TODAY}.md"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {output}")


def quality_report():
    checks = {
        "README exists": (ROOT / "README.md").exists(),
        "Workflow exists": (
            ROOT / ".github" / "workflows" / "daily-activity.yml"
        ).exists(),
        "Python script exists": Path(__file__).exists(),
    }

    try:
        source = Path(__file__).read_text(encoding="utf-8")
        compile(source, str(__file__), "exec")
        checks["Python syntax validation"] = True
    except (SyntaxError, OSError):
        checks["Python syntax validation"] = False

    lines = [
        f"# Daily Quality Report - {TODAY}",
        "",
        "## Validation results",
        "",
    ]

    for name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        lines.append(f"- [{status}] {name}")

    passed_count = sum(checks.values())
    failed_count = len(checks) - passed_count

    lines.extend([
        "",
        "## Summary",
        f"- Passed: {passed_count}",
        f"- Failed: {failed_count}",
    ])

    output = REPORTS / f"quality-{TODAY}.md"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {output}")

    if failed_count:
        raise SystemExit("One or more quality checks failed.")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "inventory"

    if mode == "inventory":
        inventory_report()
    elif mode == "quality":
        quality_report()
    else:
        raise SystemExit("Unknown mode. Use 'inventory' or 'quality'.")
