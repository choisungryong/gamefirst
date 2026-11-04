param(
 [string]$ProjectRoot='C:\Project\d2r-combat-baseline',
 [string]$BuildRecord='C:\Project\d2r-combat-baseline\evidence\phase4\builds\phase4-candidate-20261029-02\build.json',
 [string]$Output='C:\Project\d2r-combat-baseline\evidence\phase4\verification-gpu-20261029-02'
)
$ErrorActionPreference='Stop'
if(Test-Path -LiteralPath $Output){throw 'Use a new output path; preserve previous evidence'}
$phase4Build=Get-Content -Raw -LiteralPath $BuildRecord|ConvertFrom-Json
$phase4Manifest=Get-Content -Raw -LiteralPath $phase4Build.source_manifest|ConvertFrom-Json -AsHashtable
$phase4Exe=$phase4Build.exe
$phase4Before=@()
foreach($phase4File in $phase4Manifest.Keys){
 $phase4Actual=(Get-FileHash -LiteralPath (Join-Path $ProjectRoot $phase4File)).Hash.ToLower()
 if($phase4Actual -ne $phase4Manifest[$phase4File]){throw ('Product changed before replay: '+$phase4File)}
 $phase4Before+=[pscustomobject]@{path=$phase4File;sha256=$phase4Actual}
}
if((Get-FileHash -LiteralPath $phase4Exe).Hash.ToLower() -ne $phase4Build.exe_sha256){throw 'Executable differs from frozen receipt'}
$phase4Other=Get-CimInstance Win32_Process|Where-Object{$_.Name -match '^(Godot|D2RCombatBaseline)'}
if($phase4Other){throw 'Another Godot/game process owns the GPU'}
New-Item -ItemType Directory -Path $Output|Out-Null
$phase4Before|ConvertTo-Json|Set-Content -Encoding utf8 -LiteralPath (Join-Path $Output 'pre-replay-source.json')
$phase4Hardware=[ordered]@{os=(Get-CimInstance Win32_OperatingSystem|Select-Object Caption,Version,TotalVisibleMemorySize);cpu=(Get-CimInstance Win32_Processor|Select-Object Name,NumberOfCores,NumberOfLogicalProcessors);video=(Get-CimInstance Win32_VideoController|Select-Object Name,DriverVersion);memory_note='Video RAM is not inferred from Win32_VideoController.AdapterRAM'}
$phase4Hardware|ConvertTo-Json -Depth 4|Set-Content -Encoding utf8 -LiteralPath (Join-Path $Output 'hardware.json')
$phase4Args=@('--windowed','--resolution','1920x1080','--rendering-method','forward_plus','--rendering-driver','vulkan','--scene','res://benchmark/crowd_benchmark.tscn','--','--enemies=300','--bench-mode=fx','--bench-workload=multi_skill','--bench-warmup=10','--bench-seconds=60','--bench-phase=phase4-independent-replay',('--bench-output='+$Output.Replace('\','/')),'--bench-require-target')
[ordered]@{exe=$phase4Exe;exe_sha256=$phase4Build.exe_sha256;arguments=$phase4Args;start_utc=[DateTime]::UtcNow.ToString('o');build_record_path=$BuildRecord;source_manifest_path=$phase4Build.source_manifest;source_manifest_sha256=(Get-FileHash -LiteralPath $phase4Build.source_manifest).Hash.ToLower();embedded_preexport_manifest_sha256=$phase4Build.metadata_sha256;runner_sha256=(Get-FileHash -LiteralPath $PSCommandPath).Hash.ToLower();scope='Independent one-run replay; synthetic immortal300, real skill/status/FX, 1080p10s+60s; not original D2R or final art quality'}|ConvertTo-Json -Depth 5|Set-Content -Encoding utf8 -LiteralPath (Join-Path $Output 'launch.json')
$phase4Process=Start-Process -FilePath $phase4Exe -ArgumentList $phase4Args -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $Output 'stdout.log') -RedirectStandardError (Join-Path $Output 'stderr.log')
$phase4Clock=[Diagnostics.Stopwatch]::StartNew()
'elapsed_seconds,working_set_bytes,private_bytes'|Set-Content -Encoding utf8 -LiteralPath (Join-Path $Output 'process-memory.csv')
while(-not $phase4Process.WaitForExit(1000)){
 $phase4Process.Refresh()
 if(-not $phase4Process.HasExited){('{0:F3},{1},{2}' -f $phase4Clock.Elapsed.TotalSeconds,$phase4Process.WorkingSet64,$phase4Process.PrivateMemorySize64)|Add-Content -Encoding utf8 -LiteralPath (Join-Path $Output 'process-memory.csv')}
 if($phase4Clock.Elapsed.TotalSeconds -gt 190){if($phase4Process.Path -eq $phase4Exe){$phase4Process.Kill()};throw 'Owned replay exceeded bounded deadline'}
}
$phase4Process.WaitForExit()
$phase4After=@()
foreach($phase4File in $phase4Manifest.Keys){
 $phase4Actual=(Get-FileHash -LiteralPath (Join-Path $ProjectRoot $phase4File)).Hash.ToLower()
 $phase4After+=[pscustomobject]@{path=$phase4File;sha256=$phase4Actual;matches_pin=($phase4Actual -eq $phase4Manifest[$phase4File])}
}
$phase4After|ConvertTo-Json|Set-Content -Encoding utf8 -LiteralPath (Join-Path $Output 'post-replay-source.json')
$phase4AuditOutput=Join-Path $Output 'independent-audit.json'
& 'C:\Users\twins\AppData\Local\Programs\Python\Python310\python.exe' (Join-Path $ProjectRoot 'tests\audit_phase4_runs.py') $Output --require-goal --source-manifest $phase4Build.source_manifest --build-record $BuildRecord --output $phase4AuditOutput
$phase4AuditExit=$LASTEXITCODE
$phase4Remaining=@(Get-CimInstance Win32_Process|Where-Object{$_.Name -match '^(Godot|D2RCombatBaseline)'})
$phase4Receipt=[ordered]@{actual_exit=$phase4Process.ExitCode;audit_exit=$phase4AuditExit;exe_sha256=(Get-FileHash -LiteralPath $phase4Exe).Hash.ToLower();source_count=$phase4After.Count;source_mismatches=@($phase4After|Where-Object{-not $_.matches_pin});game_processes_remaining=$phase4Remaining.Count;stderr_bytes=(Get-Item -LiteralPath (Join-Path $Output 'stderr.log')).Length;scope='Actual owned process exit and independent raw audit are both required'}
$phase4Receipt|ConvertTo-Json -Depth 5|Set-Content -Encoding utf8 -LiteralPath (Join-Path $Output 'replay-receipt.json')
$phase4Receipt|ConvertTo-Json -Depth 5
if($phase4Process.ExitCode -ne 0 -or $phase4AuditExit -ne 0 -or $phase4After.Where({-not $_.matches_pin}).Count -gt 0 -or $phase4Remaining.Count -ne 0){exit 1}
exit 0
