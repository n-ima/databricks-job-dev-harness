# docs/01-design — 設計書一式（このハーネスの入力）

要件定義・業務設計はこのハーネスの外で完了している前提。承認済みの設計書を
ここへ配置（または正式保管先をリンク）し、索引・環境情報・IRRを整備する。

| ファイル/ディレクトリ | 役割 |
|---|---|
| `design-index.md` | 設計文書索引（唯一の入口）。AIはまずここだけを読む |
| `environment.md` | ワークスペース・カタログ・シークレット保管先・**自動化境界** |
| `irr.md` | 実装準備レビュー。`GO`/`CONDITIONAL GO`/`NO-GO` 判定（機械可読マーカー付き） |
| `requirements/` | 要件文書（ある場合のみ） |
| `basic-design/` | 基本設計（アーキテクチャ・外部設計） |
| `detailed-design/features/` | 機能別詳細設計（1機能1ファイル） |
| `detailed-design/common/` | 共通機能の詳細設計 |

作成順: `/01-design-intake`（索引+環境）→ `/02-design-check`（品質チェック+IRR）。
`*_template.md` は直接編集せず、コピーして実体ファイルを作る。
