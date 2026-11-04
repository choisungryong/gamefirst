param(
 [string]$ProjectRoot='C:\Project\d2r-combat-baseline',
 [string]$BuildRecord='C:\Project\d2r-combat-baseline\evidence\phase5\builds\phase5-candidate-20261029-01\build.json',
 [string]$Output='C:\Project\d2r-combat-baseline\evidence\phase5\verification-gpu-20261030-01'
)
$ErrorActionPreference='Stop'
if(Test-Path -LiteralPath $Output){throw 'Use a new output path; preserve previous evidence'}
$phase5Build=Get-Content -Raw -LiteralPath $BuildRecord|ConvertFrom-Json
$phase5Manifest=Get-Content -Raw -LiteralPath $phase5Build.source_manifest|ConvertFrom-Json -AsHashtable
$phase5Exe=$phase5Build.exe
$phase5Before=@()
foreach($phase5File in $phase5Manifest.Keys){
 $phase5Actual=(Get-FileHash -LiteralPath (Join-Path $ProjectRoot $phase5File)).Hash.ToLower()
 if($phase5Actual -ne $phase5Manifest[$phase5File]){throw ('Product changed before replay: '+$phase5File)}
 $phase5Before+=[pscustomobject]@{path=$phase5File;sha256=$phase5Actual}
}
if((Get-FileHash -LiteralPath $phase5Exe).Hash.ToLower() -ne $phase5Build.exe_sha256){throw 'Executable differs from frozen receipt'}
$phase5Other=Get-CimInstance Win32_Process|Where-Object{$_.Name -match '^(Godot|D2RCombatBaseline)'}
if($phase5Other){throw 'Another Godot/game process owns the GPU'}
New-Item -ItemType Directory -Path $Output|Out-Null
$phase5Before|ConvertTo-Json|Set-Content -Encoding utf8 -LiteralPath (Join-Path $Output 'pre-replay-source.json')
$phase5Hardware=[ordered]@{os=(Get-CimInstance Win32_OperatingSystem|Select-Object Caption,Version,TotalVisibleMemorySize);cpu=(Get-CimInstance Win32_Processor|Select-Object Name,NumberOfCores,NumberOfLogicalProcessors);video=(Get-CimInstance Win32_VideoController|Select-Object Name,DriverVersion);memory_note='Video RAM is not inferred from Win32_VideoController.AdapterRAM'}
$phase5Hardware|ConvertTo-Json -Depth 4|Set-Content -Encoding utf8 -LiteralPath (Join-Path $Output 'hardware.json')
$phase5Args=@('--windowed','--resolution','1920x1080','--rendering-method','forward_plus','--rendering-driver','vulkan','--scene','res://benchmark/crowd_benchmark.tscn','--','--enemies=300','--bench-mode=fx','--bench-workload=multi_skill','--bench-equipment','--bench-warmup=10','--bench-seconds=60','--bench-phase=phase5-independent-replay',('--bench-output='+$Output.Replace('\','/')),'--bench-require-target')
[ordered]@{exe=$phase5Exe;exe_sha256=$phase5Build.exe_sha256;arguments=$phase5Args;start_utc=[DateTime]::UtcNow.ToString('o');build_record_path=$BuildRecord;source_manifest_path=$phase5Build.source_manifest;source_manifest_sha256=(Get-FileHash -LiteralPath $phase5Build.source_manifest).Hash.ToLower();embedded_preexport_manifest_sha256=$phase5Build.metadata_sha256;runner_sha256=(Get-FileHash -LiteralPath $PSCommandPath).Hash.ToLower();scope='Independent one-run replay; synthetic highHP300 with three equipped items and owner level2, real skill/status/FX, 1080p10s+60s; not original D2R or final art quality'}|ConvertTo-Json -Depth 5|Set-Content -Encoding utf8 -LiteralPath (Join-Path $Output 'launch.json')
$phase5Process=Start-Process -FilePath $phase5Exe -ArgumentList $phase5Args -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $Output 'stdout.log') -RedirectStandardError (Join-Path $Output 'stderr.log')
$phase5Clock=[Diagnostics.Stopwatch]::StartNew()
'elapsed_seconds,working_set_bytes,private_bytes'|Set-Content -Encoding utf8 -LiteralPath (Join-Path $Output 'process-memory.csv')
while(-not $phase5Process.WaitForExit(1000)){
 $phase5Process.Refresh()
 if(-not $phase5Process.HasExited){('{0:F3},{1},{2}' -f $phase5Clock.Elapsed.TotalSeconds,$phase5Process.WorkingSet64,$phase5Process.PrivateMemorySize64)|Add-Content -Encoding utf8 -LiteralPath (Join-Path $Output 'process-memory.csv')}
 if($phase5Clock.Elapsed.TotalSeconds -gt 190){if($phase5Process.Path -eq $phase5Exe){$phase5Process.Kill()};throw 'Owned replay exceeded bounded deadline'}
}
$phase5Process.WaitForExit()
$phase5After=@()
foreach($phase5File in $phase5Manifest.Keys){
 $phase5Actual=(Get-FileHash -LiteralPath (Join-Path $ProjectRoot $phase5File)).Hash.ToLower()
 $phase5After+=[pscustomobject]@{path=$phase5File;sha256=$phase5Actual;matches_pin=($phase5Actual -eq $phase5Manifest[$phase5File])}
}
$phase5After|ConvertTo-Json|Set-Content -Encoding utf8 -LiteralPath (Join-Path $Output 'post-replay-source.json')
$phase5AuditOutput=Join-Path $Output 'independent-audit.json'
& 'C:\Users\twins\AppData\Local\Programs\Python\Python310\python.exe' (Join-Path $ProjectRoot 'tests\audit_phase5_runs.py') $Output --require-goal --source-manifest $phase5Build.source_manifest --build-record $BuildRecord --output $phase5AuditOutput
$phase5AuditExit=$LASTEXITCODE
$phase5Remaining=@(Get-CimInstance Win32_Process|Where-Object{$_.Name -match '^(Godot|D2RCombatBaseline)'})
$phase5Receipt=[ordered]@{actual_exit=$phase5Process.ExitCode;audit_exit=$phase5AuditExit;exe_sha256=(Get-FileHash -LiteralPath $phase5Exe).Hash.ToLower();source_count=$phase5After.Count;source_mismatches=@($phase5After|Where-Object{-not $_.matches_pin});game_processes_remaining=$phase5Remaining.Count;stderr_bytes=(Get-Item -LiteralPath (Join-Path $Output 'stderr.log')).Length;scope='Actual owned process exit and independent raw audit are both required'}
$phase5Receipt|ConvertTo-Json -Depth 5|Set-Content -Encoding utf8 -LiteralPath (Join-Path $Output 'replay-receipt.json')
$phase5Receipt|ConvertTo-Json -Depth 5
if($phase5Process.ExitCode -ne 0 -or $phase5AuditExit -ne 0 -or $phase5After.Where({-not $_.matches_pin}).Count -gt 0 -or $phase5Remaining.Count -ne 0){exit 1}
exit 0

