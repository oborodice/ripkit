#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""albums/*.jsonのメタデータを、rip.pyが出力した無タグFLACに適用するスクリプト。

タグ付け後、output/<アーティスト名>/<アルバム名>/ へリネームして配置する。
"""

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


@dataclass
class AlbumMetadata:
    artist: str
    album: str
    tracks: list[str]
    cover: str | None = None


def main() -> None:
    require("metaflac")
    args = parse_args()
    metadata = load_metadata(args.metadata)
    flac_files = sorted(args.rawdir.glob("track*.flac"))

    if len(flac_files) != len(metadata.tracks):
        sys.exit(
            f"error: トラック数が一致しません"
            f"(FLACファイル: {len(flac_files)}件, JSONのtracks: {len(metadata.tracks)}件)"
        )

    outdir = REPO_ROOT / "output" / sanitize(metadata.artist) / sanitize(metadata.album)
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"{len(flac_files)}トラックにタグを付与しています...")
    for track_number, (flac_path, title) in enumerate(zip(flac_files, metadata.tracks), start=1):
        set_tags(flac_path, metadata, title, track_number)
        if metadata.cover:
            embed_cover(flac_path, metadata.cover)
        dest = outdir / f"{track_number:02d} - {sanitize(title)}.flac"
        flac_path.rename(dest)
        print(f"  {dest.relative_to(REPO_ROOT)}")

    print(f"完了しました: {outdir}")


def require(cmd: str) -> None:
    if shutil.which(cmd) is None:
        sys.exit(
            f"error: '{cmd}' が見つかりません。"
            f"'brew install flac' 等でインストールしてください。"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metadata", type=Path, help="albums/<名前>.json")
    parser.add_argument("rawdir", type=Path, help="rip.pyが出力したディレクトリ")
    return parser.parse_args()


def load_metadata(path: Path) -> AlbumMetadata:
    data = json.loads(path.read_text())
    return AlbumMetadata(
        artist=data["artist"],
        album=data["album"],
        tracks=data["tracks"],
        cover=data.get("cover") or None,
    )


def sanitize(name: str) -> str:
    return name.replace("/", "-")


def set_tags(flac_path: Path, metadata: AlbumMetadata, title: str, track_number: int) -> None:
    subprocess.run(
        [
            "metaflac",
            "--remove-all-tags",
            f"--set-tag=ARTIST={metadata.artist}",
            f"--set-tag=ALBUM={metadata.album}",
            f"--set-tag=TITLE={title}",
            f"--set-tag=TRACKNUMBER={track_number}",
            str(flac_path),
        ],
        check=True,
    )


def embed_cover(flac_path: Path, cover: str) -> None:
    subprocess.run(
        ["metaflac", f"--import-picture-from={REPO_ROOT / cover}", str(flac_path)],
        check=True,
    )


if __name__ == "__main__":
    main()
