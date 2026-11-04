param(
 [string]$Exe = 'C:\Project\d2r-combat-baseline\builds\phase3\D2RCombatBaseline-phase3.exe',
 [string]$OutputRoot = 'C:\Project\d2r-combat-baseline\evidence\phase3\release-matrix',
 [string]$Schedule = 'matrix'
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
$taskExeHash = (Get-FileHash -LiteralPath $Exe).Hash
$taskInfoPath = 'C:\Project\d2r-combat-baseline\game_data\build_info.json'
$taskInfoHash = (Get-FileHash -LiteralPath $taskInfoPath).Hash
$taskCases = @()
if ($Schedule -eq 'matrix') {
 foreach($taskRenderer in @('forward_plus','gl_compatibility')) {
  foreach($taskCount in @(100,300,500)) {
   foreach($taskRepeat in @(1,2,3)) {
    $taskCases += [PSCustomObject]@{name=($taskRenderer+'-skill-n'+$taskCount+'-r'+$taskRepeat);renderer=$taskRenderer;count=$taskCount;workload='skill';seconds=60}
   }
  }
 }
} elseif ($Schedule -eq 'stress') {
 foreach($taskRepeat in @(1,2,3)) { $taskCases += [PSCustomObject]@{name=('forward_plus-bolt300-n300-r'+$taskRepeat);renderer='forward_plus';count=300;workload='projectile_stress';seconds=60} }
} elseif ($Schedule -eq 'soak') {
 $taskCases += [PSCustomObject]@{name='forward_plus-skill-n300-soak600';renderer='forward_plus';count=300;workload='skill';seconds=600}
} elseif ($Schedule -eq 'decomposition') {
 foreach($taskMode in @('sim','static','rig')) { $taskCases += [PSCustomObject]@{name=('forward_plus-'+$taskMode+'-n300-diagnostic');renderer='forward_plus';count=300;workload='projectile_stress';seconds=8;mode=$taskMode} }
} else { throw 'Unknown schedule' }
$taskResults = @()
foreach($taskCase in $taskCases) {
 if ((Get-FileHash -LiteralPath $Exe).Hash -ne $taskExeHash -or (Get-FileHash -LiteralPath $taskInfoPath).Hash -ne $taskInfoHash) { throw 'Build artifact or metadata changed during the measured schedule' }
 $taskOut = Join-Path $OutputRoot $taskCase.name
 if (Test-Path -LiteralPath $taskOut) { throw ('Preserve prior evidence; output already exists: '+$taskOut) }
 New-Item -ItemType Directory -Path $taskOut | Out-Null
 $taskMode = 'fx'
 if ($taskCase.PSObject.Properties.Name -contains 'mode') { $taskMode=$taskCase.mode }
 $taskDriver = 'vulkan'
 if ($taskCase.renderer -eq 'gl_compatibility') { $taskDriver='opengl3' }
 $taskOutputArg = $taskOut.Replace('\','/')
 $taskArguments = @('--windowed','--resolution','1920x1080','--rendering-method',$taskCase.renderer,'--rendering-driver',$taskDriver,'--scene','res://benchmark/crowd_benchmark.tscn','--',('--enemies='+$taskCase.count),('--bench-mode='+$taskMode),('--bench-workload='+$taskCase.workload),'--bench-bolts=300','--bench-warmup=10',('--bench-seconds='+$taskCase.seconds),'--bench-phase=final-release',('--bench-output='+$taskOutputArg))
 [ordered]@{exe=$Exe;exe_sha256=$taskExeHash;embedded_preexport_manifest_sha256=$taskInfoHash;arguments=$taskArguments;start_utc=[DateTime]::UtcNow.ToString('o');scope='Standalone release, instrumented synthetic highHP/mana fixture; original semantics and rendered workload declared in summary'} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskOut 'launch.json') -Encoding utf8
 $taskProcess = Start-Process -FilePath $Exe -ArgumentList $taskArguments -WindowStyle Normal -PassThru -RedirectStandardOutput (Join-Path $taskOut 'stdout.log') -RedirectStandardError (Join-Path $taskOut 'stderr.log')
 $taskClock = [Diagnostics.Stopwatch]::StartNew()
 $taskRamPath = Join-Path $taskOut 'process-memory.csv'
 'elapsed_seconds,working_set_bytes,private_bytes' | Set-Content -LiteralPath $taskRamPath -Encoding utf8
 while(-not $taskProcess.WaitForExit(1000)) {
  try { $taskProcess.Refresh(); if(-not $taskProcess.HasExited) { ('{0:F3},{1},{2}' -f $taskClock.Elapsed.TotalSeconds,$taskProcess.WorkingSet64,$taskProcess.PrivateMemorySize64) | Add-Content -LiteralPath $taskRamPath -Encoding utf8 } } catch {}
  if($taskClock.Elapsed.TotalSeconds -gt ($taskCase.seconds+180)) {
   if($taskProcess.Path -eq $Exe) { $taskProcess.Kill() }
   throw ('Owned benchmark exceeded timeout: '+$taskCase.name)
  }
 }
 $taskProcess.WaitForExit()
 $taskExit = $taskProcess.ExitCode
 $taskSummaryPath = Join-Path $taskOut 'summary.json'
 if(-not (Test-Path -LiteralPath $taskSummaryPath)) { throw ('Missing benchmark summary: '+$taskCase.name+' exit '+$taskExit) }
 $taskSummary = Get-Content -LiteralPath $taskSummaryPath -Raw | ConvertFrom-Json
 $taskResult = [PSCustomObject]@{name=$taskCase.name;exit=$taskExit;valid=$taskSummary.valid_run;target_eligible=$taskSummary.target_eligible;target_pass=$taskSummary.target_pass;p95_ms=$taskSummary.frame_ms.p95;sim_alive_min=$taskSummary.sim_alive.min;rigs_min=$taskSummary.skinned_rigs.min;sample_seconds=$taskSummary.measured_sample_seconds;exe_sha256=$taskExeHash;metadata_matches=($taskSummary.embedded_source_manifest_sha256 -eq $taskInfoHash.ToLower());source_hashes_basis=$taskSummary.source_hashes_basis}
 $taskResults += $taskResult
 $taskResults | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $OutputRoot 'schedule-results.json') -Encoding utf8
 Write-Output ($taskResult | ConvertTo-Json -Compress)
}
if($taskResults.Where({$_.exit -ne 0 -or -not $_.valid -or -not $_.metadata_matches}).Count -gt 0) { exit 1 }
exit 0

