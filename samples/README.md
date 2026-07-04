# samples — ハーネス動作確認用のサンプル設計書一式

ハーネスを初めて使うとき・改修後に通しでテストするときの題材。
**日次売上レポート作成ジョブ**（CSV取込 → Delta登録 → 検証 → 集計 → CSV出力、
直列4タスクDAG）を、実装まで到達できる粒度の設計書として用意してある。

| ファイル | 内容 |
|---|---|
| `design-docs/basic-design/BD-001_...md` | 基本設計書（テーブル設計・Job DAG・冪等性方針） |
| `design-docs/detailed-design/features/DD-001_ingest.md` | 入力取込（AC-101〜103） |
| `design-docs/detailed-design/features/DD-002_validate.md` | データ検証（AC-201〜203） |
| `design-docs/detailed-design/features/DD-003_aggregate.md` | 店舗別日次集計（AC-301〜303） |
| `design-docs/detailed-design/features/DD-004_export.md` | レポート出力（AC-401〜403） |
| `test-data/sales_20260701.csv` | 検証用入力データ（正常9行 + 不正6行） |

## テスト手順

1. **案件リポジトリを用意する**（USAGE.md 0節。テンプレート/ZIPから作成。
   ハーネス本体リポジトリの上で直接試す場合は、終了後に `git clean` で戻すこと）。
2. サンプル設計書を配置する:

   ```bash
   cp samples/design-docs/basic-design/*.md docs/01-design/basic-design/
   cp samples/design-docs/detailed-design/features/*.md docs/01-design/detailed-design/features/
   ```

3. Copilot Chatで `/00-start-project` → `/01-design-intake`。
   索引には BD-001 / DD-001〜004 を登録する（版1.0・承認日2026-07-04・
   受け入れ条件IDは各DDに記載済み）。`environment.md` は実ワークスペースの値で埋める。
4. **devリソースを準備する**（catalog/schemaは environment.md の値に読み替え）:

   ```bash
   databricks sql-query   # または任意のSQL実行手段で:
   #   CREATE SCHEMA IF NOT EXISTS <catalog>.<schema>;
   #   CREATE VOLUME IF NOT EXISTS <catalog>.<schema>.landing;
   databricks fs cp samples/test-data/sales_20260701.csv \
     dbfs:/Volumes/<catalog>/<schema>/landing/input/sales_20260701.csv
   ```

5. 新しいチャットで `/02-design-check` → `GO`（環境値が未確定なら `CONDITIONAL GO`）を確認。
6. `/03-implementation-plan` → `/04-implement-task`（リネームT-000を含む。
   `resources/main.job.yml` の4タスクDAG化もタスクに含まれる）→ 自動で `/05-test`。
   テストフェーズが devデプロイ → `processing_date=2026-07-01` でのJob実行 →
   結合テスト → 再実行（冪等性）まで自動で行う。

## 期待結果（答え合わせ）

`processing_date = 2026-07-01`、入力15行に対して:

| 項目 | 期待値 |
|---|---|
| sales_raw | 15行 |
| sales_clean | 9行 / sales_rejected | 6行（不合格率40% → E-201は発動しない） |
| 不合格の内訳 | quantity_out_of_range(S0006), missing:product_code(S0007), duplicate_sale_id(S0003の2件目), date_mismatch(S0008), unit_price_out_of_range(S0009), invalid_quantity(S0010) |
| sales_daily_summary | 3行 |
| 出力CSV | ヘッダ+3行、store_code昇順 |

出力CSVのデータ行:

```csv
2026-07-01,ST01,2500,4,3
2026-07-01,ST02,13000,9,3
2026-07-01,ST03,14400,7,3
```

**同一パラメータで再実行しても上記がすべて同一になること**（冪等性）まで確認して合格。

## 後片付け

```bash
databricks bundle destroy -t dev    # Hooksのask確認が入る（正常な動作）
# 必要なら DROP SCHEMA <catalog>.<schema> CASCADE;
```
