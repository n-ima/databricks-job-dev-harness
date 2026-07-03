# Agent Hooks — ゲート・セキュリティ・本番保護の機械的強制（Preview）

Hooksはモデルを介さないシェル実行であり、ほぼゼロコストでルールを強制できる。
`AGENTS.md` の指示レベルのルールと二重の安全網を構成する
（Preview機能のため、発火しない環境でも指示レベルのルールが効くようにしてある）。

## 構成

| ファイル | イベント | 内容 |
|---|---|---|
| `gate-hooks.json` | PreToolUse | `guard-template-edit`（`*_template.md` 直接編集をdeny）/ `guard-dangerous-git`（push/tag/force/rm -rf をask）/ `guard-databricks-prod`（下記） |
| | SessionStart | `inject-progress`（GATE_STATUS + **IRR判定** + 教訓ログを自動注入） |
| | PreCompact | `inject-progress PreCompact`（コンテキスト圧縮でゲート状態・IRR判定・教訓が失われないよう同じ内容を再注入） |
| | PostToolUse | `warn-stale-gate`（承認済み文書の編集を検知して非ブロッキング警告） |
| `security-hooks.json` | PreToolUse | `guard-harness-config-edit`（agents/hooks/workflows/AGENTS.md等の編集をdeny）/ `guard-secret-leak`（Databricks PAT `dapi...` 等の高確度パターンをdeny、汎用パターンをask） |

## guard-databricks-prod（このハーネス固有）

| 操作 | 判定 |
|---|---|
| `databricks bundle deploy/run -t dev` | 素通し（全自動区間） |
| `databricks bundle deploy/run -t staging` / `-t prod` | **ask**（人の承認ポイント） |
| `databricks bundle destroy`、`jobs delete`、`schemas delete` 等の破壊的操作 | **ask**（強い警告つき） |

devターゲットを素通しにしているのは、テストフェーズの「devデプロイ→実Job実行→結合テスト」を
人の確認なしで回すため（`DECISIONS.md` D-006）。本番保護はこのフックに加えて
GitHub Environments（required reviewers）とDatabricks側の権限分離
（開発用IDにprod書き込み権限を与えない）の三重で担保する。**フックだけを最終防壁にしない。**

## IRR判定の注入（inject-progress）

`docs/01-design/irr.md` の `IRR_VERDICT:` マーカー（機械可読）をパースし、
セッション開始時に判定値を注入する。`GO`/`CONDITIONAL_GO` 以外の場合は
「プロダクションコードの実装・変更は禁止」という注意も同時に注入する。
マーカーの書式は `irr_template.md` を参照（キー名・形式を崩さないこと）。

## 動作確認

- VS CodeのOutputパネル → GitHub Copilot Chat Hooks でロード状態を確認する。
- ChatのCustomization Diagnosticsでも読み込みを確認できる。
- Windowsは `windows:` キーのPowerShellスクリプト、macOS/Linuxはbashスクリプトが使われる。
- ペイロード形状が想定外の場合、すべてのスクリプトは安全側（継続許可）に倒れる。
  denyが必要な保護はブランチ保護・CODEOWNERS・環境権限でも重ねること。
