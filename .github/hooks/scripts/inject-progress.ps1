# SessionStart / PreCompact hook: フェーズゲート状況(GATE_STATUS)・IRR判定・
# 教訓ログ(learnings)を会話開始時に自動注入する。PreCompactでも同じ内容を再注入し、
# コンテキスト圧縮でゲート状態・IRR判定が失われないようにする。
# 第1引数でイベント名を受け取る(既定: SessionStart)。
param([string]$EventName = "SessionStart")
$ErrorActionPreference = 'SilentlyContinue'
$progress = "docs/00-overview/progress.md"
$irr = "docs/01-design/irr.md"
$learnings = "docs/00-overview/learnings.md"

$ctx = ""
if (Test-Path $progress) {
  $lines = Get-Content $progress -Raw
  $match = [regex]::Match($lines, '(?s)<!-- GATE_STATUS.*?-->')
  $block = if ($match.Success) { $match.Value } else { "" }
  $ctx = "現在のフェーズゲート状況(docs/00-overview/progress.md):`n$block"
} else {
  $ctx = "docs/00-overview/progress.md が未作成です。まず /00-start-project を実行してください。"
}

if (Test-Path $irr) {
  $irrText = Get-Content $irr -Raw
  $vm = [regex]::Match($irrText, 'IRR_VERDICT:\s*([A-Z_]+)')
  if ($vm.Success) {
    $verdict = $vm.Groups[1].Value
    $ctx += "`n`nIRR判定(docs/01-design/irr.md): $verdict"
    if ($verdict -ne "GO" -and $verdict -ne "CONDITIONAL_GO") {
      $ctx += "`n注意: IRRがGO/CONDITIONAL GOでないため、プロダクションコード(src/, resources/, databricks.yml)の実装・変更は禁止です(AGENTS.md参照)。"
    }
  }
} else {
  $ctx += "`n`nIRR(docs/01-design/irr.md)が未作成です。実装前に /02-design-check を完了してください。"
}

if (Test-Path $learnings) {
  # 「## 教訓」以降の箇条書きだけを注入する(先頭50行まで。肥大化してもコンテキストを圧迫しないため)
  $content = Get-Content $learnings
  $flag = $false
  $lessons = @()
  foreach ($line in $content) {
    if ($line -match '^## 教訓') { $flag = $true; continue }
    if ($flag -and $line -match '^- ') { $lessons += $line }
    if ($lessons.Count -ge 50) { break }
  }
  if ($lessons.Count -gt 0) {
    $ctx += "`n`nこのプロジェクトの教訓(docs/00-overview/learnings.md、必ず前提として扱うこと):`n" + ($lessons -join "`n")
  }
}

$out = @{
  hookSpecificOutput = @{
    hookEventName = $EventName
    additionalContext = $ctx
  }
}
$out | ConvertTo-Json -Depth 5 -Compress
