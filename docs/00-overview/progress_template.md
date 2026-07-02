<!-- GATE_STATUS
design_check: not_started
implementation: not_started
test: not_started
release: not_started
-->

# 進捗ダッシュボード

最終更新日: YYYY-MM-DD

上のコメントブロック（GATE_STATUS）が正の状態。`.github/hooks/` のフックや
`.github/skills/gate-check/SKILL.md` はこのブロックを直接パースするため、
書き換えるときはキー名・インデントを崩さないこと。

| フェーズ | 状態 | ゲート承認日 | 備考 |
|---|---|---|---|
| 設計書チェック（登録+品質+IRR） | 未着手 | - | IRR判定: 未実施 |
| 実装（計画+実装） | 未着手 | - | |
| テスト（devデプロイ・実Job実行含む） | 未着手 | - | |
| リリース（staging/prod） | 未着手 | - | |

状態は次のいずれか: `未着手`(not_started) / `進行中`(in_progress) / `ゲート承認待ち`(pending_approval) / `完了`(done)

## 未確定事項・申し送り

- （フェーズ間で持ち越す未解決の疑問点や前提をここに記録する）
