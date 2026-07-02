# テスト計画

観点の分類は `.github/skills/databricks-job-testing/SKILL.md` を参照。
すべてのテストケースを設計ID・受け入れ条件IDに対応づける。

## 対象

| 項目 | 内容 |
|---|---|
| 対象設計ID | TODO |
| 対象コミット/ブランチ | TODO |
| devターゲット（catalog.schema） | TODO |
| テストデータ方針 | 合成 / 匿名化（実データ・個人情報は使わない） |

## テストケース

| ID | 層 | 観点（正常/境界/異常/再実行/品質/性能） | 設計ID / 受け入れ条件 | 合格基準（数値） | 実装先 |
|---|---|---|---|---|---|
| TC-001 | 単体 | 正常 | DD-001 / AC-001 | TODO | tests/unit/test_TODO.py |
| TC-002 | 結合 | データ品質（件数・主キー一意・NULL率） | DD-001 / AC-002 | TODO | tests/integration/test_TODO.py |
| TC-003 | 結合 | 冪等性（同一Job 2回実行） | DD-001 / AC-003 | 1回目と結果一致 | tests/integration/test_TODO.py |

## 実行手順（段階実行。前段が失敗したら先へ進まない）

1. `uv run task check`
2. `uv run task build`
3. `databricks bundle validate -t dev`
4. `databricks bundle deploy -t dev`
5. `databricks bundle run <job_key> -t dev`（run IDを記録）
6. `uv run task integration`
7. （受け入れ条件にあれば）再実行による冪等性の実証
