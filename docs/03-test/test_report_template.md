# テスト結果報告

実行していない検証を成功と報告しない。実データの行・個人情報を貼らない
（マスキング済みのschema・error class・run IDで記録する）。

## サマリ

| 項目 | 内容 |
|---|---|
| 実施日 | YYYY-MM-DD |
| 対象コミット | TODO（SHA） |
| 結果 | TODO（合格 / 不合格 / 条件付き） |
| 独立レビュー（reviewer） | TODO（問題なし / 要対応 — 詳細は security-review-report.md） |

## 段階実行の結果

| 段階 | コマンド | 結果 | 証跡（run ID等） |
|---|---|---|---|
| 静的検査+単体 | `uv run task check` | TODO | - |
| ビルド | `uv run task build` | TODO | - |
| Bundle検証 | `databricks bundle validate -t dev` | TODO | - |
| devデプロイ | `databricks bundle deploy -t dev` | TODO | - |
| 実Job実行 | `databricks bundle run <job> -t dev` | TODO | run ID: TODO |
| 結合テスト | `uv run task integration` | TODO | - |
| 冪等性実証 | 再実行 + 検証 | TODO / 該当なし | run ID: TODO |

## テストケース結果

| ID | 結果 | 実測値（合格基準との比較） | 備考 |
|---|---|---|---|
| TC-001 | TODO | TODO | |

## 不具合と対応

| ID | 内容 | 切り分け（実装バグ / テスト誤り / 仕様判断要） | 対応 | 状態 |
|---|---|---|---|---|
| - | 該当なし | - | - | - |

## 残存リスク・申し送り

- TODO / 該当なし
