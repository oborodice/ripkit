# ripkit

音楽CDをFLACとしてリッピングするためのスクリプト

## 使い方

- macOS
- [Homebrew](https://brew.sh/)
- [uv](https://docs.astral.sh/uv/)

```bash
$ brew install libcdio-paranoia flac
```

- CDドライブに音楽CDを挿入し、以下を実行する

```bash
# 全トラックを無タグのFLACとして抽出する
$ ./rip.py
```
