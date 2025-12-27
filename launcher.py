#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

DEFAULT_CONFIG = {
    "repo_url": "",
    "addons_subdir": "",
    "addons_dir": "",
    "branch": "main",
    "shallow": True,
}


def load_config(config_path: Path) -> dict:
    if not config_path.exists():
        return DEFAULT_CONFIG.copy()
    with config_path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    merged = DEFAULT_CONFIG.copy()
    merged.update({k: v for k, v in data.items() if v is not None})
    return merged


def save_config(config_path: Path, config: dict) -> None:
    with config_path.open("w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def run_git(args, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=str(cwd), check=True)


def clone_or_update_repo(repo_url: str, repo_dir: Path, branch: str, shallow: bool) -> None:
    if repo_dir.exists():
        run_git(["fetch", "origin", branch], repo_dir)
        run_git(["reset", "--hard", f"origin/{branch}"], repo_dir)
        return
    repo_dir.parent.mkdir(parents=True, exist_ok=True)
    clone_args = ["clone", repo_url, str(repo_dir), "--branch", branch]
    if shallow:
        clone_args.extend(["--depth", "1"])
    run_git(clone_args, Path.cwd())


def sync_addons(source_dir: Path, target_dir: Path) -> None:
    if not source_dir.exists():
        raise FileNotFoundError(f"Source addons directory not found: {source_dir}")
    target_dir.mkdir(parents=True, exist_ok=True)
    for item in source_dir.iterdir():
        if item.name.startswith("."):
            continue
        dest = target_dir / item.name
        if dest.exists():
            if dest.is_dir() and item.is_dir():
                shutil.rmtree(dest)
            else:
                dest.unlink()
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)


def expand_path(path_str: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(path_str))).resolve()


def configure(args) -> None:
    config_path = Path("config.json")
    config = load_config(config_path)
    if args.repo_url:
        config["repo_url"] = args.repo_url
    if args.addons_subdir is not None:
        config["addons_subdir"] = args.addons_subdir
    if args.addons_dir:
        config["addons_dir"] = args.addons_dir
    if args.branch:
        config["branch"] = args.branch
    if args.no_shallow:
        config["shallow"] = False
    save_config(config_path, config)
    print(f"Saved configuration to {config_path}")


def update(args) -> None:
    config_path = Path("config.json")
    config = load_config(config_path)
    repo_url = args.repo_url or config.get("repo_url")
    if not repo_url:
        raise SystemExit("repo_url is required. Set it via --repo-url or config.json")
    addons_dir = args.addons_dir or config.get("addons_dir")
    if not addons_dir:
        raise SystemExit("addons_dir is required. Set it via --addons-dir or config.json")
    addons_subdir = args.addons_subdir
    if addons_subdir is None:
        addons_subdir = config.get("addons_subdir", "")
    branch = args.branch or config.get("branch", "main")
    shallow = config.get("shallow", True)
    if args.no_shallow:
        shallow = False

    repo_dir = Path(".addons_repo")
    clone_or_update_repo(repo_url, repo_dir, branch, shallow)

    source_dir = repo_dir
    if addons_subdir:
        source_dir = repo_dir / addons_subdir
    target_dir = expand_path(addons_dir)
    sync_addons(source_dir, target_dir)
    print(f"Addons updated in {target_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="WoW addons launcher/updater that syncs addons from a Git repo."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    configure_parser = subparsers.add_parser("configure", help="Save default settings")
    configure_parser.add_argument("--repo-url", help="Git repository URL")
    configure_parser.add_argument(
        "--addons-subdir",
        help="Subdirectory in the repo that contains addons (optional)",
    )
    configure_parser.add_argument(
        "--addons-dir",
        help="Local WoW Interface/AddOns directory",
    )
    configure_parser.add_argument("--branch", help="Git branch", default=None)
    configure_parser.add_argument(
        "--no-shallow",
        action="store_true",
        help="Disable shallow clone",
    )
    configure_parser.set_defaults(func=configure)

    update_parser = subparsers.add_parser("update", help="Update addons from repo")
    update_parser.add_argument("--repo-url", help="Git repository URL")
    update_parser.add_argument(
        "--addons-subdir",
        help="Subdirectory in the repo that contains addons (optional)",
        default=None,
    )
    update_parser.add_argument(
        "--addons-dir",
        help="Local WoW Interface/AddOns directory",
    )
    update_parser.add_argument("--branch", help="Git branch", default=None)
    update_parser.add_argument(
        "--no-shallow",
        action="store_true",
        help="Disable shallow clone",
    )
    update_parser.set_defaults(func=update)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
