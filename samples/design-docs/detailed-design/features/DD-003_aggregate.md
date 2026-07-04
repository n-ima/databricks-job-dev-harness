# 詳細設計書: 店舗別日次集計（aggregate）

| 項目 | 内容 |
|---|---|
| 設計ID | DD-003 |
| 版 | 1.0 / 承認日 2026-07-04（サンプル） |
| 上位設計 | BD-001 / 前段: DD-002 |

## 1. 機能概要

`sales_clean` の当日分を店舗単位に集計し、`sales_daily_summary` へ登録する。

## 2. 入力

- `<catalog>.<schema>.sales_clean` のうち `processing_date = パラメータ値` の行

## 3. 出力

`<catalog>.<schema>.sales_daily_summary`（無ければ作成。`processing_date` 洗い替え）

| 列 | 型 | 算出方法 |
|---|---|---|
| processing_date | date | パラメータ値 |
| store_code | string | グループキー |
| total_amount | long | Σ (quantity × unit_price) |
| total_quantity | long | Σ quantity |
| detail_count | long | 明細行数 |

## 4. 処理仕様

1. 当日分の `sales_clean` を読み込む。
2. `store_code` でグループ化し、上表の3指標を算出する。
3. 冪等性: `sales_daily_summary` の当日分をDELETEしてINSERTする。
4. 集計対象が0件の場合は当日分0行（洗い替えのみ）で**正常終了**し、警告ログを出す。
5. 店舗数・合計金額の総和をINFOログに出力する。

## 5. エラー処理

本タスク固有の業務エラーはない（入力不備は前段DD-002で除去済み）。
想定外の例外は異常終了とし、Jobの失敗通知に委ねる。

## 6. 受け入れ条件

| ID | 条件 | 確認方法 |
|---|---|---|
| AC-301 | 集計値（total_amount / total_quantity / detail_count）が入力明細からの手計算と一致する。1店舗1明細（境界）と複数明細の合算の両方で確認 | 単体+結合テスト |
| AC-302 | 同一 `processing_date` で再実行しても `sales_daily_summary` の内容が同一（行の重複なし） | 結合テスト: 2回実行して比較 |
| AC-303 | 当日分の合格明細が0件のとき、当日分0行で正常終了する | 単体テスト |

## 7. 実装・テスト指針

- 集計ロジック（明細リスト → 店舗別集計）はSpark非依存の純粋関数として実装し、
  AC-301の境界ケースを単体テストで担保する。金額計算はint演算（円）で行い、
  浮動小数点を使わない。
