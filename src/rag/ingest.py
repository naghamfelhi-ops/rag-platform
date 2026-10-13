import hashlib
import json
import subprocess
from pathlib import Path

import yaml

RAW = Path("data/raw")
MANIFEST = Path("data/processed/manifest.json")


def load_config(path="configs/config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)


def clone_or_update(name, url):
    target = RAW / name
    if target.exists():
        subprocess.run(["git", "-C", str(target), "pull", "--ff-only"], check=True)
    else:
        subprocess.run(["git", "clone", "--depth", "1", url, str(target)], check=True)
    return target


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect_markdown(repo_dir, docs_path):
    return sorted((repo_dir / docs_path).rglob("*.md"))


def run():
    cfg = load_config()
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    old = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    new, changed = {}, []

    for repo in cfg["corpus"]["repos"]:
        repo_dir = clone_or_update(repo["name"], repo["url"])
        for f in collect_markdown(repo_dir, repo["docs_path"]):
            key = str(f)
            new[key] = file_hash(f)
            if old.get(key) != new[key]:
                changed.append(key)

    MANIFEST.write_text(json.dumps(new, indent=2))
    print(f"{len(new)} fichiers au total, {len(changed)} nouveaux ou modifiés")
    return changed


if __name__ == "__main__":
    run()