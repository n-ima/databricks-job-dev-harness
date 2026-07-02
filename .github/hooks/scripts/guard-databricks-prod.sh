#!/usr/bin/env bash
# PreToolUse hook: Databricks CLIの本番影響・破壊的操作を保護する。
# - bundle destroy / jobs delete 等の破壊的操作: ask(強い警告つき)
# - staging/prodターゲットへのbundle deploy/run: ask(人の承認ポイント)
# - devターゲットは全自動区間のため対象外(確認を挟まない)。
input=$(cat)
cmd=$(printf '%s' "$input" | grep -oE '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed -E 's/.*:[[:space:]]*"([^"]*)"/\1/')

if [[ -z "$cmd" ]] || ! printf '%s' "$cmd" | grep -Eiq 'databricks'; then
  printf '%s\n' '{"continue": true}'
  exit 0
fi

destructive='bundle[[:space:]]+destroy|jobs[[:space:]]+delete|workspace[[:space:]]+delete|schemas[[:space:]]+delete|tables[[:space:]]+delete|volumes[[:space:]]+delete|secrets[[:space:]]+delete'
prod_target='(bundle[[:space:]]+(deploy|run|destroy)).*(((-t|--target)[[:space:]]+)(staging|prod))'

if printf '%s' "$cmd" | grep -Eiq "$destructive"; then
  printf '%s\n' '{"continue": true, "systemMessage": "Databricksリソースの破壊的操作(destroy/delete)を検出しました。復旧できない可能性があります。", "hookSpecificOutput": {"permissionDecision": "ask", "permissionDecisionReason": "破壊的なDatabricks操作のため、人の確認が必要です。"}}'
elif printf '%s' "$cmd" | grep -Eiq "$prod_target"; then
  printf '%s\n' '{"continue": true, "systemMessage": "staging/prodターゲットへのBundle操作はAGENTS.mdの方針により人の承認が必要です(devは自動化境界内)。", "hookSpecificOutput": {"permissionDecision": "ask", "permissionDecisionReason": "本番系環境への変更のため、人の承認ポイントです。"}}'
else
  printf '%s\n' '{"continue": true}'
fi
