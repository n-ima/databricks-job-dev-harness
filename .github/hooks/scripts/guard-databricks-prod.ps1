# PreToolUse hook: Databricks CLIの本番影響・破壊的操作を保護する。
# - bundle destroy / jobs delete 等の破壊的操作: ask(強い警告つき)
# - staging/prodターゲットへのbundle deploy/run: ask(人の承認ポイント)
# - devターゲットは全自動区間のため対象外(確認を挟まない)。
$ErrorActionPreference = 'SilentlyContinue'
$raw = [Console]::In.ReadToEnd()
$cmd = $null
try {
  $obj = $raw | ConvertFrom-Json
  $cmd = $obj.tool_input.command
} catch {
  if ($raw -match '"command"\s*:\s*"([^"]*)"') {
    $cmd = $Matches[1]
  }
}

if (-not $cmd -or $cmd -notmatch 'databricks') {
  @{ continue = $true } | ConvertTo-Json -Compress
  exit 0
}

$destructive = 'bundle\s+destroy|jobs\s+delete|workspace\s+delete|schemas\s+delete|tables\s+delete|volumes\s+delete|secrets\s+delete'
$prodTarget = '(bundle\s+(deploy|run|destroy)).*(((-t|--target)\s+)(staging|prod))'

if ($cmd -match $destructive) {
  $out = @{
    continue = $true
    systemMessage = "Databricksリソースの破壊的操作(destroy/delete)を検出しました。復旧できない可能性があります。"
    hookSpecificOutput = @{
      permissionDecision = "ask"
      permissionDecisionReason = "破壊的なDatabricks操作のため、人の確認が必要です。"
    }
  }
} elseif ($cmd -match $prodTarget) {
  $out = @{
    continue = $true
    systemMessage = "staging/prodターゲットへのBundle操作はAGENTS.mdの方針により人の承認が必要です(devは自動化境界内)。"
    hookSpecificOutput = @{
      permissionDecision = "ask"
      permissionDecisionReason = "本番系環境への変更のため、人の承認ポイントです。"
    }
  }
} else {
  $out = @{ continue = $true }
}
$out | ConvertTo-Json -Depth 5 -Compress
