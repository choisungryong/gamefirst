param(
 [Parameter(Mandatory=$true)][string]$Exe,
 [Parameter(Mandatory=$true)][string]$OutputRoot,
 [string]$BuildManifestPath='',
 [ValidateSet('smoke','main')][string]$Schedule='smoke'
)
$ErrorActionPreference='Stop'
if (Test-Path -LiteralPath $OutputRoot) { throw 'Preserve previous evidence; choose a new output root' }
if (-not (Test-Path -LiteralPath $Exe)) { throw 'Executable missing' }
$taskRunning = Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(Godot|D2RCombatBaseline)' }
if ($taskRunning) { throw 'Another Godot/game process is active; coordinate GPU ownership first' }
New-Item -ItemType Directory -Path $OutputRoot | Out-Null
$taskHash=(Get-FileHash -LiteralPath $Exe).Hash.ToLower()
if (-not $BuildManifestPath) { $BuildManifestPath=Join-Path 'C:\Project\d2r-combat-baseline\evidence\phase5\builds' ((Split-Path -Leaf (Split-Path -Parent $Exe))+'\source-manifest.json') }
if (-not (Test-Path -LiteralPath $BuildManifestPath)) { throw 'Frozen source manifest missing' }
$taskManifestHash=(Get-FileHash -LiteralPath $BuildManifestPath).Hash.ToLower()
$taskManifest=Get-Content -LiteralPath $BuildManifestPath -Raw | ConvertFrom-Json
$taskMetadataHash=$taskManifest.'game_data/build_info.json'
$taskBuildPath=Join-Path (Split-Path -Parent $BuildManifestPath) 'build.json'
$taskBuild=Get-Content -LiteralPath $taskBuildPath -Raw | ConvertFrom-Json
if ($taskBuild.exe_sha256 -ne $taskHash) { throw 'Executable does not match frozen build receipt' }
$taskWarmup=2
$taskSeconds=8
$taskRepeats=1
if ($Schedule -eq 'main') { $taskWarmup=10; $taskSeconds=60; $taskRepeats=3 }
$taskResults=@()
foreach ($taskRepeat in 1..$taskRepeats) {
 if ((Get-FileHash -LiteralPath $Exe).Hash.ToLower() -ne $taskHash) { throw 'Executable changed during schedule' }
 if ((Get-FileHash -LiteralPath $BuildManifestPath).Hash.ToLower() -ne $taskManifestHash) { throw 'Manifest changed during schedule' }
 $taskOut=Join-Path $OutputRoot ('forward-plus-multi-skill-n300-r'+$taskRepeat)
 New-Item -ItemType Directory -Path $taskOut | Out-Null
 $taskArgs=@('--windowed','--resolution','1920x1080','--rendering-method','forward_plus','--rendering-driver','vulkan','--scene','res://benchmark/crowd_benchmark.tscn','--','--enemies=300','--bench-mode=fx','--bench-workload=multi_skill','--bench-equipment',('--bench-warmup='+$taskWarmup),('--bench-seconds='+$taskSeconds),('--bench-phase=phase5-'+$Schedule),('--bench-output='+$taskOut.Replace('\','/')))
 if ($Schedule -eq 'main') { $taskArgs+='--bench-require-target' }
 [ordered]@{exe=$Exe;exe_sha256=$taskHash;build_manifest_path=$BuildManifestPath;source_manifest_sha256=$taskManifestHash;embedded_preexport_manifest_sha256=$taskMetadataHash;build_receipt_path=$taskBuildPath;arguments=$taskArgs;start_utc=[DateTime]::UtcNow.ToString('o');scope='Independent phase5 round robin with three equipped items and explicit owner level2, common resolver, real status and FX; finite boosted-HP synthetic crowd'} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskOut 'launch.json') -Encoding utf8
 $taskProcess=Start-Process -FilePath $Exe -ArgumentList $taskArgs -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $taskOut 'stdout.log') -RedirectStandardError (Join-Path $taskOut 'stderr.log')
 $taskClock=[Diagnostics.Stopwatch]::StartNew()
 'elapsed_seconds,working_set_bytes,private_bytes' | Set-Content -LiteralPath (Join-Path $taskOut 'process-memory.csv') -Encoding utf8
 while (-not $taskProcess.WaitForExit(1000)) {
  $taskProcess.Refresh()
  if (-not $taskProcess.HasExited) { ('{0:F3},{1},{2}' -f $taskClock.Elapsed.TotalSeconds,$taskProcess.WorkingSet64,$taskProcess.PrivateMemorySize64) | Add-Content -LiteralPath (Join-Path $taskOut 'process-memory.csv') -Encoding utf8 }
  if ($taskClock.Elapsed.TotalSeconds -gt ($taskWarmup+$taskSeconds+120)) { if ($taskProcess.Path -eq $Exe) { $taskProcess.Kill() }; throw 'Owned benchmark timed out' }
 }
 $taskProcess.WaitForExit()
 $taskSummaryPath=Join-Path $taskOut 'summary.json'
 if (-not (Test-Path -LiteralPath $taskSummaryPath)) { throw ('Missing summary; exit '+$taskProcess.ExitCode) }
 $taskSummary=Get-Content -LiteralPath $taskSummaryPath -Raw | ConvertFrom-Json
 if ($taskSummary.embedded_source_manifest_sha256 -ne $taskMetadataHash) { throw 'Runtime embedded source metadata differs from frozen build' }
 $taskResult=[ordered]@{name=(Split-Path -Leaf $taskOut);exit=$taskProcess.ExitCode;valid=$taskSummary.valid_run;eligible=$taskSummary.target_eligible;target_pass=$taskSummary.target_pass;p95_ms=$taskSummary.frame_ms.p95;sample_seconds=$taskSummary.measured_sample_seconds;framebuffer=@($taskSummary.framebuffer_width,$taskSummary.framebuffer_height);skills=$taskSummary.sample_skill_event_counts;combat_errors=$taskSummary.combat_errors;exe_sha256=$taskHash}
 $taskResults += [PSCustomObject]$taskResult
 $taskResults | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $OutputRoot 'schedule-results.json') -Encoding utf8
 $taskResult | ConvertTo-Json -Depth 8 -Compress | Write-Output
}
if ($taskResults.Where({$_.exit -ne 0 -or -not $_.valid}).Count -gt 0) { exit 1 }
exit 0

