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

- `albums/<名前>.json`にアーティスト名・アルバム名・曲名を記載し、以下を実行する

```bash
# タグを付与し、output/<アーティスト名>/<アルバム名>/ へ配置する
$ ./tag.py albums/<名前>.json output/.raw/<タイムスタンプ>
```
