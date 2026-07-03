#!/usr/bin/env bash
# SessionStart / PreCompact hook: フェーズゲート状況(GATE_STATUS)・IRR判定・
# 教訓ログ(learnings)を会話開始時に自動注入する。PreCompactでも同じ内容を再注入し、
# コンテキスト圧縮でゲート状態・IRR判定が失われないようにする。
# 第1引数でイベント名を受け取る(既定: SessionStart)。
event="${1:-SessionStart}"
progress="docs/00-overview/progress.md"
irr="docs/01-design/irr.md"
learnings="docs/00-overview/learnings.md"

ctx=""
if [[ -f "$progress" ]]; then
  block=$(awk '/<!-- GATE_STATUS/,/-->/' "$progress")
  ctx="現在のフェーズゲート状況(docs/00-overview/progress.md):\n${block}"
else
  ctx="docs/00-overview/progress.md が未作成です。まず /00-start-project を実行してください。"
fi

if [[ -f "$irr" ]]; then
  verdict=$(grep -oE 'IRR_VERDICT:[[:space:]]*[A-Z_]+' "$irr" | head -1 | sed -E 's/IRR_VERDICT:[[:space:]]*//')
  if [[ -n "$verdict" ]]; then
    ctx="${ctx}\n\nIRR判定(docs/01-design/irr.md): ${verdict}"
    if [[ "$verdict" != "GO" && "$verdict" != "CONDITIONAL_GO" ]]; then
      ctx="${ctx}\n注意: IRRがGO/CONDITIONAL GOでないため、プロダクションコード(src/, resources/, databricks.yml)の実装・変更は禁止です(AGENTS.md参照)。"
    fi
  fi
else
  ctx="${ctx}\n\nIRR(docs/01-design/irr.md)が未作成です。実装前に /02-design-check を完了してください。"
fi

if [[ -f "$learnings" ]]; then
  # 「## 教訓」以降の箇条書きだけを注入する(先頭50行まで。肥大化してもコンテキストを圧迫しないため)
  lessons=$(awk '/^## 教訓/{flag=1;next}flag' "$learnings" | grep -E '^- ' | head -50)
  if [[ -n "$lessons" ]]; then
    ctx="${ctx}\n\nこのプロジェクトの教訓(docs/00-overview/learnings.md、必ず前提として扱うこと):\n${lessons}"
  fi
fi

esc=$(printf '%b' "$ctx" | sed ':a;N;$!ba;s/\n/\\n/g' | sed 's/"/\\"/g')
printf '{"hookSpecificOutput": {"hookEventName": "%s", "additionalContext": "%s"}}\n' "$event" "$esc"
