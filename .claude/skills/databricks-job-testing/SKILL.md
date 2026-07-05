---
name: databricks-job-testing
description: Databricks Jobのテストケース設計と段階実行の手順。単体(Spark非依存)/結合(devデプロイ後)/データ品質/冪等性/性能の観点分類、合成データの作り方、テスト計画作成時に使う。
---

# Databricks Jobテスト設計スキル

## テストの層構造（下から順に速く・安く・多く）

| 層 | 置き場所 | 実行環境 | 検証対象 |
|---|---|---|---|
| 単体 | `tests/unit/` | ローカル（Spark非依存） | 業務ルールの純粋関数。正常・境界・異常・再入力 |
| Bundle検証 | - | ローカル | `databricks bundle validate -t dev`（構文・参照整合） |
| 実Job実行 | - | devターゲット | `bundle deploy` → `bundle run`。DAG・パラメータ・権限が実際に通ること |
| 結合 | `tests/integration/`（`integration` marker） | devターゲット | 出力データの検証（下記データ品質） |
| 冪等性 | 結合に含める | devターゲット | 同一Jobの再実行で結果が重複・破損しないこと |
| 性能 | 必要な場合のみ | dev/staging | IRRで数値化した規模・閾値で計測 |

## テストケース設計の観点

1. **受け入れ条件起点**: 各設計IDの受け入れ条件を1つ以上のテストに対応づける
   （`traceability.md` に記録）。実装からテストを逆算しない（写経テスト禁止）。
2. **データ品質の合格基準を数値で**: 件数（期待±許容）、主キー一意、NULL率、
   参照整合性、値域。IRRで数値化した基準をそのままassertにする。
3. **バッチJob固有の異常系**: 入力が空/欠損/重複/遅延して届く、途中失敗からの再実行、
   同時二重起動（`max_concurrent_runs` の検証）、月末月初・うるう年・タイムゾーン境界。
4. **冪等性の実証**: 「再実行しても安全」は設計書の主張であり、テストで実証する。
   同じパラメータで2回実行し、出力の件数・内容が1回目と一致する（または設計どおり
   上書きされる）ことを確認する。
5. **合成データのみ**: テストデータは合成または匿名化済みとし、個人情報・実データを
   使わない。結合テストはdevカタログの専用schemaのみに書き込み、production dataへ
   接続しない。
6. **Spark依存ロジックのローカル検証（任意）**: 純粋関数に分離しきれない
   Spark変換ロジックは、databricks-connect（VS Code Databricks拡張のデバッグ機能）で
   devクラスタに接続してローカルから実行検証できる。使う場合も自動テストとしては
   `tests/integration/`（markerつき）に置き、単体テスト層をSpark依存にしない。

## 実行手順（テストフェーズの段階実行）

```bash
uv run task check                       # 1. format/lint/mypy/単体テスト
uv run task build                       # 2. wheelビルド
databricks bundle validate -t dev       # 3. Bundle構文・参照整合
databricks bundle deploy -t dev         # 4. devへデプロイ（自動化境界内）
databricks bundle run <job_key> -t dev  # 5. 実Job実行（run IDを記録）
uv run task integration                 # 6. 出力データの結合テスト
# 7. 冪等性: 5を再実行し、6の結果が設計どおりであることを確認
```

前段が失敗したら先に進まない。run ID・実測値は `docs/03-test/test-report.md` に記録する。

## 結合テスト実装の既知の落とし穴

- **Serverless SQL Warehouseのcold start**: 初回クエリがPENDINGのままタイムアウトして
  テストが偽陰性になる。SQL実行ヘルパーには「PENDING/RUNNINGの間は最大120秒程度
  ポーリングして完了を待つ」ロジックを必ず入れる（検証プロジェクトで実証済みの対策）。
- **異常系の明示チェック**: 入力ファイル不存在などの想定異常は、Spark内部例外任せに
  せず実装側で明示チェック（存在確認→設計のエラーIDに対応するメッセージで失敗）に
  なっていることをテストで確認する。内部例外依存だとエラーメッセージが検証できない。

## やってはいけないこと

- テストを通すためにassertを緩める・skipする・カバレッジ除外に逃がす。
- 実データの行をテストコード・レポート・プロンプトに貼る。
- 単体テストの成功だけで「動作確認済み」と報告する（実Job実行までがテスト）。
