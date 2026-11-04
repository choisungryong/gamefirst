param(
 [string]$EvidenceRoot = 'C:\Project\d2r-combat-baseline\evidence\phase3',
 [string]$ControlDirectory = 'C:\Project\d2r-combat-baseline\evidence\phase3\resume-20261028-control'
)
$ErrorActionPreference = 'Stop'
$taskRunner = Join-Path $PSScriptRoot 'resume_phase3_schedule.ps1'
$taskStages = @(
 [pscustomobject]@{name='matrix';output='release-matrix-resume-20261028';prior=(Join-Path $EvidenceRoot 'release-matrix')},
 [pscustomobject]@{name='stress';output='release-stress-20261028';prior=''},
 [pscustomobject]@{name='soak';output='release-soak-20261028';prior=''},
 [pscustomobject]@{name='decomposition';output='release-decomposition-20261028';prior=''}
)
$taskStageResults = @()
try {
 foreach ($taskStage in $taskStages) {
  $taskDestination = Join-Path $EvidenceRoot $taskStage.output
  $taskStarted = [DateTime]::UtcNow.ToString('o')
  Write-Output ('STAGE_START '+$taskStage.name+' '+$taskStarted)
  & $taskRunner -OutputRoot $taskDestination -Schedule $taskStage.name -PriorOutputRoot $taskStage.prior
  $taskExit = $LASTEXITCODE
  $taskStageResults += [pscustomobject]@{schedule=$taskStage.name;directory=$taskDestination;started_utc=$taskStarted;finished_utc=[DateTime]::UtcNow.ToString('o');exit=$taskExit}
  $taskStageResults | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $ControlDirectory 'stage-results.json') -Encoding utf8
  if ($taskExit -ne 0) { throw ('Schedule integrity or execution failed: '+$taskStage.name) }
 }
 [ordered]@{success=$true;finished_utc=[DateTime]::UtcNow.ToString('o');scope='Finite continuation: remaining15 matrix cases +3 projectile stress +1 ten-minute soak +3 diagnostic decompositions. Prior evidence preserved.'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $ControlDirectory 'completion.json') -Encoding utf8
 exit 0
} catch {
 [ordered]@{success=$false;failed_utc=[DateTime]::UtcNow.ToString('o');error=$_.Exception.Message} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $ControlDirectory 'completion.json') -Encoding utf8
 throw
}
