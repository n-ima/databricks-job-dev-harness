---
applyTo: "tests/**/*.py"
---

# テストコード固有ルール

- Spark・ワークスペース・デプロイ済みリソースを必要としないテストは `tests/unit/`、
  必要とするテストは `tests/integration/`（`@pytest.mark.integration` 必須）に置く。
- テストは受け入れ条件から書く。実装の写経（実装と同じロジックで期待値を計算する等）に
  しない。`docs/02-implementation/traceability.md` で設計IDと対応づける。
- 各変更に正常・境界・異常・再実行のうち関係する観点を含める。
  ファイル名は対象機能に対応する `test_<feature>.py` を標準とする。
- テストデータは合成または匿名化済みのみ。個人情報・実データの行を含めない。
- 結合テストはdevカタログの専用schemaのみに書き込み、production dataへ接続しない。
- テストを通すためにassertを緩めない・skipで逃がさない・カバレッジ除外に逃がさない。
