---
name: gate-check
description: docs/00-overview/progress.md のGATE_STATUS(design_check/implementation/test/release)を判定・更新する手順。IRRの判定値と連動させる。オーケストレーターや各フェーズエージェントが進捗確認・更新するときに使う。
---

# ゲート判定スキル

## 状態の正

`docs/00-overview/progress.md` の先頭にある機械可読ブロックが正。人間向けの表と
必ず一致させる。

```
<!-- GATE_STATUS
design_check: not_started | in_progress | pending_approval | done
implementation: not_started | in_progress | pending_approval | done
test: not_started | in_progress | pending_approval | done
release: not_started | in_progress | pending_approval | done
-->
```

## 判定手順

1. `docs/00-overview/progress.md` が無ければ `progress_template.md` から作成する。
2. 各フェーズについて、対応する成果物ファイルの有無・内容から実態を推測する。
   - design_check: `docs/01-design/design-index.md` が無ければ `not_started`。
     索引・`environment.md` があれば `in_progress`。`irr.md` の判定が
     `GO`/`CONDITIONAL GO` で承認記録があり、ユーザー承認を得ていれば `done`。
     **`NO-GO` は `done` にできない。**
   - implementation: `docs/02-implementation/tasks.md`（全チェックボックス完了で `done`）
   - test: `docs/03-test/test-report.md`（独立レビュー結果の記載があって `done`）
   - release: `docs/04-release/release-checklist.md`（production承認記録があって `done`）
3. GATE_STATUSブロックと実態がずれていれば、ユーザーに更新してよいか確認してから書き換える
   （エージェントが黙って `done` にしない。ユーザーの明示的な承認発言があって初めて
   `done` にする）。「未着手/進行中」への修正は機械的に判断できるため確認不要。
4. `design_check` が `done` でない間は、implementation以降のフェーズを開始しない
   （`AGENTS.md` の「IRRが未判定またはNO-GOの間、プロダクションコードを実装しない」に対応）。
5. `.github/hooks/scripts/` のゲート系フックはこのGATE_STATUSブロックを直接パースするため、
   フォーマット（インデント・キー名）を崩さない。
