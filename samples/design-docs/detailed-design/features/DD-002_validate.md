# 詳細設計書: データ検証（validate）

| 項目 | 内容 |
|---|---|
| 設計ID | DD-002 |
| 版 | 1.0 / 承認日 2026-07-04（サンプル） |
| 上位設計 | BD-001 / 前段: DD-001 |

## 1. 機能概要

`sales_raw` の当日分を検証し、合格行を型付きで `sales_clean` へ、不合格行を
理由つきで `sales_rejected` へ登録する。

## 2. 入力

- `<catalog>.<schema>.sales_raw` のうち `processing_date = パラメータ値` の行

## 3. 出力

- 合格: `<catalog>.<schema>.sales_clean`（BD-001 4.2の型に変換して登録）
- 不合格: `<catalog>.<schema>.sales_rejected`（入力6列string + `reject_reason` + `processing_date`）
- いずれも無ければ作成。冪等性: 両テーブルとも `processing_date` 洗い替え

## 4. 検証ルール（上から順に評価し、最初に該当した理由を `reject_reason` とする）

| # | ルール | reject_reason |
|---|---|---|
| 1 | 6列すべて非NULLかつ空文字でない | `missing:<列名>` |
| 2 | sale_date が `YYYY-MM-DD` として妥当な日付 | `invalid_date` |
| 3 | quantity が整数に変換可能 | `invalid_quantity` |
| 4 | unit_price が整数に変換可能 | `invalid_unit_price` |
| 5 | quantity >= 1 | `quantity_out_of_range` |
| 6 | unit_price >= 0 | `unit_price_out_of_range` |
| 7 | sale_date = processing_date | `date_mismatch` |
| 8 | sale_id が当日分の中で一意（2件目以降を不合格。1件目は合格） | `duplicate_sale_id` |

## 5. 処理仕様

1. 当日分の `sales_raw` を読み込む。0件なら警告ログを出して正常継続
   （clean/rejectedとも当日分0件に洗い替え）。
2. 各行に検証ルールを適用し、合格/不合格に振り分ける。
3. **不合格率チェック**: 不合格行数 ÷ 入力行数 が 0.5 を超える場合、
   両テーブルへの書き込みは行ったうえで異常終了する（E-201。入力データ異常の疑い）。
4. 合格・不合格の件数と不合格理由別内訳をINFOログに出力する。

## 6. エラー処理

| ID | 事象 | 動作 |
|---|---|---|
| E-201 | 不合格率 > 50% | 書き込み後に異常終了。メッセージに率と理由内訳を含める |

## 7. 受け入れ条件

| ID | 条件 | 確認方法 |
|---|---|---|
| AC-201 | 合格行数 + 不合格行数 = 入力行数（欠落・重複計上なし） | 結合テスト |
| AC-202 | 不合格行すべてに検証ルール表どおりの `reject_reason` が入る | 単体+結合テスト |
| AC-203 | 不合格率が50%を超えた場合、書き込み後に異常終了する | 単体テスト（境界: ちょうど50%は正常） |

## 8. 実装・テスト指針

- 検証ルール（1行の判定関数、重複判定、不合格率判定）はSpark非依存の純粋関数とし、
  ルール1〜8それぞれに単体テストを書く（正常・境界・異常）。
