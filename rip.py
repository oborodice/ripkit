#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""汎用CDリッピングスクリプト。特定のアルバムの情報は一切持たない。

CDドライブから全トラックを抽出し、無タグのFLACとして
output/.raw/<timestamp>/ に保存する。
"""

import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def main() -> None:
    require("cd-paranoia")
    require("flac")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = REPO_ROOT / "output" / ".raw" / timestamp
    outdir.mkdir(parents=True)

    print(f"CDを読み取っています... (出力先: {outdir})")
    rip_exit = rip_tracks(outdir)
    if rip_exit != 0:
        print(
            f"warning: cd-paranoiaが正常終了しませんでした(exit {rip_exit})。"
            f"{outdir / 'rip.log'} で読み取りエラーの有無を確認してください。",
            file=sys.stderr,
        )

    wav_files = sorted(outdir.glob("*.cdda.wav"))
    if not wav_files:
        sys.exit(
            "error: トラックが抽出できませんでした。"
            "ドライブが認識されているか 'cd-paranoia --analyze-drive' で確認してください。"
        )

    print(f"{len(wav_files)}トラックをFLACへエンコードしています...")
    encode_to_flac(wav_files)

    print(f"完了しました。抽出結果: {outdir}")
    print("次は albums/<名前>.json を用意し、以下を実行してください:")
    print(f"  ./tag.py albums/<名前>.json {outdir}")


def require(cmd: str) -> None:
    if shutil.which(cmd) is None:
        sys.exit(
            f"error: '{cmd}' が見つかりません。"
            f"'brew install libcdio-paranoia' 等でインストールしてください。"
        )


def rip_tracks(outdir: Path) -> int:
    """cd-paranoiaでディスクを読み取り、進捗をrip.logへも書き出す。戻り値はcd-paranoiaの終了コード。"""
    log_path = outdir / "rip.log"
    with log_path.open("w") as log:
        proc = subprocess.Popen(
            ["cd-paranoia", "--batch"],
            cwd=outdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            print(line, end="", flush=True)
            log.write(line)
        proc.wait()
        return proc.returncode


def encode_to_flac(wav_files: list[Path]) -> None:
    for wav in wav_files:
        flac_path = wav_to_flac_path(wav)
        subprocess.run(
            [
                "flac",
                "--best",
                "--verify",
                "--silent",
                f"--output-name={flac_path}",
                str(wav),
            ],
            check=True,
        )
        wav.unlink()


def wav_to_flac_path(wav: Path) -> Path:
    # 拡張子を2回剥がすことで "track01.cdda.wav" -> "track01.flac" にする
    # (with_suffixは末尾の拡張子1つしか置き換えられないため)
    return wav.with_suffix("").with_suffix(".flac")


if __name__ == "__main__":
    main()
