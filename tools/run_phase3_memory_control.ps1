param(
 [Parameter(Mandatory=$true)][string]$OutputRoot,
 [double]$Seconds = 300,
 [double]$Warmup = 10
)
$ErrorActionPreference = 'Stop'
if (-not [double]::IsFinite($Seconds) -or $Seconds -lt 2 -or $Seconds -gt 300 -or -not [double]::IsFinite($Warmup) -or $Warmup -lt 0 -or $Warmup -gt 10) { throw 'Invalid finite control duration/warmup' }
if (Test-Path -LiteralPath $OutputRoot) { throw 'Preserve previous control evidence; choose a new output directory' }
$taskExe='C:\Project\d2r-combat-baseline\builds\phase3\D2RCombatBaseline-phase3.exe'
$taskScript=Join-Path $PSScriptRoot 'phase3_memory_control.gd'
$taskHash=(Get-FileHash -LiteralPath $taskExe).Hash
if ($taskHash -ne '76BBB630424B7A2F2D65C6587C781ADDEC58D6A1C63D39C59396316A9D2CBFAD') { throw 'The final EXE differs from the frozen artifact' }
New-Item -ItemType Directory -Path $OutputRoot|Out-Null
$taskOut=$OutputRoot.Replace('\','/')
$taskArgs=@('--windowed','--resolution','1920x1080','--rendering-method','forward_plus','--rendering-driver','vulkan','--script',$taskScript,'--','--enemies=300','--bench-mode=fx','--bench-workload=skill','--bench-bolts=300',('--bench-warmup='+$Warmup),'--bench-seconds=3600','--bench-phase=memory-retention-control',('--bench-output='+$taskOut),('--control-output='+$taskOut),('--control-seconds='+$Seconds))
[ordered]@{exe=$taskExe;exe_sha256=$taskHash;external_script=$taskScript;external_script_sha256=(Get-FileHash -LiteralPath $taskScript).Hash;runner=$PSCommandPath;runner_sha256=(Get-FileHash -LiteralPath $PSCommandPath).Hash;arguments=$taskArgs;started_utc=[DateTime]::UtcNow.ToString('o');scope='Non-performance matched memory control; only the embedded benchmark numeric row retention is reclaimed every1s'}|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $OutputRoot 'launch.json') -Encoding utf8
$taskProcess=Start-Process -FilePath $taskExe -ArgumentList $taskArgs -WindowStyle Normal -PassThru -RedirectStandardOutput (Join-Path $OutputRoot 'stdout.log') -RedirectStandardError (Join-Path $OutputRoot 'stderr.log')
[ordered]@{pid=$taskProcess.Id;exe=$taskExe}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $OutputRoot 'owner.json') -Encoding utf8
$taskClock=[Diagnostics.Stopwatch]::StartNew()
$taskMemoryPath=Join-Path $OutputRoot 'process-memory.csv'
'elapsed_seconds,working_set_bytes,private_bytes'|Set-Content -LiteralPath $taskMemoryPath -Encoding utf8
while(-not $taskProcess.WaitForExit(1000)) {
 try {$taskProcess.Refresh(); if(-not $taskProcess.HasExited){('{0:F3},{1},{2}' -f $taskClock.Elapsed.TotalSeconds,$taskProcess.WorkingSet64,$taskProcess.PrivateMemorySize64)|Add-Content -LiteralPath $taskMemoryPath -Encoding utf8}} catch {}
 if($taskClock.Elapsed.TotalSeconds -gt $Seconds+$Warmup+120){if($taskProcess.Path -eq $taskExe){$taskProcess.Kill()};throw 'Owned memory control exceeded its finite timeout'}
}
$taskProcess.WaitForExit()
$taskCode=$taskProcess.ExitCode
$taskReport=Join-Path $OutputRoot 'control-report.json'
if(-not(Test-Path -LiteralPath $taskReport)){throw ('Missing control report, exit '+$taskCode)}
$taskData=Get-Content -LiteralPath $taskReport -Raw|ConvertFrom-Json
if(Test-Path -LiteralPath (Join-Path $OutputRoot 'summary.json')){throw 'A formal performance summary was emitted during the control'}
[ordered]@{exit=$taskCode;success=$taskData.success;actual_sample_seconds=$taskData.actual_sample_seconds;clear_count=$taskData.clear_count;clear_state_unchanged=$taskData.clear_state_unchanged;exe_unchanged=((Get-FileHash -LiteralPath $taskExe).Hash -eq $taskHash);finished_utc=[DateTime]::UtcNow.ToString('o')}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $OutputRoot 'execution.json') -Encoding utf8
Get-Content -LiteralPath (Join-Path $OutputRoot 'execution.json') -Raw
exit $(if($taskCode -eq 0 -and $taskData.success){0}else{1})
