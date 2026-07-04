# 基本設計書: 日次売上レポート作成ジョブ（daily-sales-report）

| 項目 | 内容 |
|---|---|
| 設計ID | BD-001 |
| 版 | 1.0 |
| 承認日 | 2026-07-04 |
| 作成 / 承認 | 情報システム部 設計G / 部長承認済み（サンプル） |
| 関連 | DD-001, DD-002, DD-003, DD-004 |

## 変更履歴

| 版 | 日付 | 内容 |
|---|---|---|
| 1.0 | 2026-07-04 | 初版承認 |

## 1. 目的・背景

各店舗のPOSから日次で連携される売上明細CSVを取り込み、検証・集計のうえ
店舗別日次売上サマリのCSVレポートを作成する。従来の手作業集計を廃止し、
再実行可能なバッチとして自動化する。

## 2. スコープ

- 対象: 売上明細CSVの取込、検証、店舗別日次集計、レポートCSV出力
- **対象外（将来対応）**: スケジュール起動（当面は手動またはテスト起動。
  timezone・SLA確定後に別途設計）、月次集計、BIダッシュボード連携、
  過去日の一括バックフィル（単日指定の再実行で代替する）

## 3. システム構成

- 実行基盤: Databricks Job（Databricks Asset Bundlesで管理。UI恒久変更禁止）
- データ格納: Unity Catalog 配下のDeltaテーブルおよびVolume
- 環境分離: catalog / schema はBundle変数（`${var.catalog}` / `${var.schema}`）に従う。
  コードへの直書き禁止
- 入出力ファイル置き場（Unity Catalog Volume）:
  - 入力: `/Volumes/<catalog>/<schema>/landing/input/`
  - 出力: `/Volumes/<catalog>/<schema>/landing/output/`
  - Volume名は `landing` とし、初回セットアップで作成する（運用手順参照）

## 4. データ設計

### 4.1 入力ファイル

`sales_<YYYYMMDD>.csv`（UTF-8、ヘッダあり、カンマ区切り。YYYYMMDDは処理対象日）

| 列 | 型（論理） | 例 | 備考 |
|---|---|---|---|
| sale_id | 文字列 | S0001 | 明細ID。同一処理日内で一意 |
| store_code | 文字列 | ST01 | 店舗コード |
| sale_date | 日付(YYYY-MM-DD) | 2026-07-01 | 処理対象日と一致すること |
| product_code | 文字列 | P100 | 商品コード |
| quantity | 整数 | 2 | 1以上 |
| unit_price | 整数（円） | 500 | 0以上 |

### 4.2 テーブル一覧（すべて `<catalog>.<schema>` 配下のDeltaテーブル）

| テーブル | 役割 | 主な列 |
|---|---|---|
| sales_raw | 取込生データ（全列文字列 + 取込メタ） | 入力6列（string）, processing_date date, source_file string, ingest_ts timestamp |
| sales_clean | 検証合格データ（型付き） | sale_id string, store_code string, sale_date date, product_code string, quantity int, unit_price int, processing_date date |
| sales_rejected | 検証不合格データ | 入力6列（string）, reject_reason string, processing_date date |
| sales_daily_summary | 店舗別日次集計 | processing_date date, store_code string, total_amount long, total_quantity long, detail_count long |

テーブルが存在しない場合は初回実行時に作成する（CREATE TABLE IF NOT EXISTS 相当）。

## 5. ジョブ設計

### 5.1 タスクDAG（直列4タスク）

```
ingest（DD-001） → validate（DD-002） → aggregate（DD-003） → export（DD-004）
```

- 各タスクは同一wheelパッケージの別エントリポイントとして実装する
  （`resources/main.job.yml` を4タスク構成へ改修する。depends_onで直列化）
- 前段タスクが失敗した場合、後続タスクは実行しない

### 5.2 パラメータ

| パラメータ | 型 | 既定値 | 説明 |
|---|---|---|---|
| processing_date | 文字列(YYYY-MM-DD) | なし（必須） | 処理対象日。手動/テスト起動時に明示指定する |
| catalog / schema | 文字列 | Bundle変数 | 環境分離用 |

### 5.3 実行制御（テンプレートの既定を踏襲）

- 同時実行: `max_concurrent_runs: 1`（同一日付の二重起動防止はこれで担保）
- タイムアウト: 3600秒 / リトライ: タスクごとに `max_retries: 2`
- compute: classic job cluster 1 worker（Runtime・node typeは `environment.md` の承認値。
  serverless移行はIRRで別途判断）

## 6. 冪等性方針（全タスク共通）

- 各Deltaテーブルへの書き込みは **processing_date単位の洗い替え**
  （同一processing_dateの既存行をDELETEしてからINSERT）とする
- 出力CSVは同名ファイルを上書きする
- したがって同一processing_dateでの再実行は、何度実行しても最終状態が同一になる

## 7. エラー処理・監視

- 業務エラー（入力ファイル不存在、不合格率超過）は日本語メッセージつきで異常終了し、
  Jobの失敗通知（`notification_email` 変数）で運用へ連絡する
- ログには件数・処理日・ファイル名のみ出力する。**明細データの値はログに出力しない**
- 一次対応・復旧はRunbook（開発ハーネスのリリースフェーズで作成）に従う

## 8. 性能・データ量

- 想定データ量: 日次最大10万行（サンプル検証は十数行）
- 実行時間目標: 全タスク合計15分以内（10万行時）

## 9. セキュリティ

- 本ジョブが扱うデータに個人情報は含まれない（店舗・商品コードのみ）
- テーブル・Volumeへの権限はUnity Catalogで最小権限付与（閲覧はjob_viewer_group）

## 10. 受け入れ条件

受け入れ条件（AC-1xx〜AC-4xx）は各詳細設計書に記載し、本書はIDの索引のみ持つ。
DD-001: AC-101〜103 / DD-002: AC-201〜203 / DD-003: AC-301〜303 / DD-004: AC-401〜403
