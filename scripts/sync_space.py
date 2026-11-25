"""Rebuild this Static Space from a clean checkout of its canonical Git commit."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "SOURCE.json"
SHARED = "https://github.com/AceDataCloud/SunoHuggingFace"
FILES = {"AGENTS.md", "LICENSE", "PRIVACY.md", "README.md", "README_zh_Hans.md", "client.mjs", "index.html", "styles.css"}
FOLDERS = {"assets", "docs", "studio"}


def artifact_path(name):
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or (name not in FILES and path.parts[0] not in FOLDERS):
        raise ValueError(f"Unexpected Space file {name!r}")
    return ROOT / path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Checkout of AceDataCloud/SunoHuggingFace")
    parser.add_argument("--update", action="store_true", help="Copy generated files and update the source pin")
    options = parser.parse_args()
    checkout = options.source.resolve()

    def git(*args):
        return subprocess.check_output(["git", "-C", str(checkout), *args], text=True).strip()

    if git("status", "--porcelain", "--untracked-files=all"):
        parser.error("Use a clean canonical checkout; the commit must identify every source file.")
    commit = git("rev-parse", "HEAD")
    previous = json.loads(SOURCE.read_text()) if SOURCE.is_file() else {}
    if not options.update and commit != previous.get("revision"):
        parser.error("Check out the revision recorded in SOURCE.json before verification.")
    subprocess.run([sys.executable, "scripts/build_spaces.py"], cwd=checkout, check=True)
    subprocess.run([sys.executable, "scripts/check_space_packages.py"], cwd=checkout, check=True)
    archive = checkout / "artifacts/acemusic-static-space.zip"
    with zipfile.ZipFile(archive) as package:
        names = sorted(package.namelist())
        manifest = {"repository": SHARED, "revision": commit,
                    "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(), "files": names}
        if options.update:
            for name in set(previous.get("files", [])) - set(names):
                artifact_path(name).unlink(missing_ok=True)
        elif previous != manifest:
            parser.error("The generated archive differs from its pinned digest or inventory.")
        for name in names:
            target = artifact_path(name)
            data = package.read(name)
            if options.update:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            elif not target.is_file() or target.read_bytes() != data:
                parser.error(f"{name} differs from the canonical build.")
        if options.update:
            SOURCE.write_text(json.dumps(manifest, indent=2) + "\n")
    output = ROOT / "artifacts" / archive.name
    output.parent.mkdir(exist_ok=True)
    shutil.copyfile(archive, output)
    print(f"Verified {len(names)} files at {commit}; standalone archive: {output}")


if __name__ == "__main__":
    main()
