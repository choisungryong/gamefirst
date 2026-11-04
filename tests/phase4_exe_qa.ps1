param(
 [string]$ProjectRoot='C:\Project\d2r-combat-baseline',
 [string]$BuildRecord='C:\Project\d2r-combat-baseline\evidence\phase4\builds\phase4-candidate-20261029-02\build.json',
 [string]$Output='C:\Project\d2r-combat-baseline\evidence\phase4\final-exe-qa-20261029-02'
)
$ErrorActionPreference='Stop'
if(Test-Path -LiteralPath $Output){throw 'Use a new output path; preserve all prior QA'}
$phase4Build=Get-Content -Raw -LiteralPath $BuildRecord|ConvertFrom-Json
$phase4Source=Get-Content -Raw -LiteralPath $phase4Build.source_manifest|ConvertFrom-Json -AsHashtable
foreach($phase4File in $phase4Source.Keys){if((Get-FileHash -LiteralPath (Join-Path $ProjectRoot $phase4File)).Hash.ToLower() -ne $phase4Source[$phase4File]){throw ('Frozen product changed: '+$phase4File)}}
if((Get-FileHash -LiteralPath $phase4Build.exe).Hash.ToLower() -ne $phase4Build.exe_sha256){throw 'Frozen executable changed'}
if(Get-CimInstance Win32_Process|Where-Object{$_.Name -match '^(Godot|D2RCombatBaseline)'}){throw 'Another renderer is active'}
New-Item -ItemType Directory -Path $Output|Out-Null
$phase4Cases=@(@{name='fire-n0';count=0;skill='skill.ember_bolt'},@{name='fire-n1';count=1;skill='skill.ember_bolt'},@{name='fire-n10';count=10;skill='skill.ember_bolt'},@{name='fire-n100';count=100;skill='skill.ember_bolt'},@{name='cold-n10';count=10;skill='skill.frost_pulse'},@{name='chain-n10';count=10;skill='skill.arc_chain'})
$phase4Results=@()
foreach($phase4Case in $phase4Cases){
 if(Get-CimInstance Win32_Process|Where-Object{$_.Name -match '^(Godot|D2RCombatBaseline)'}){throw 'Another renderer is active between QA cases'}
 $phase4Directory=Join-Path $Output $phase4Case.name
 New-Item -ItemType Directory -Path $phase4Directory|Out-Null
 $phase4Frame=Join-Path $phase4Directory 'frame.png'
 $phase4CaptureAt=1.25
 if($phase4Case.skill -eq 'skill.frost_pulse'){$phase4CaptureAt=.45}
 if($phase4Case.skill -eq 'skill.arc_chain'){$phase4CaptureAt=.30}
 $phase4Args=@('--windowed','--resolution','1920x1080','--rendering-method','forward_plus','--rendering-driver','vulkan','--','--qa',('--enemies='+$phase4Case.count),('--skill='+$phase4Case.skill),'--quit-after=3',('--capture-at='+$phase4CaptureAt),('--capture='+$phase4Frame.Replace('\','/')),('--report='+$phase4Directory.Replace('\','/')))
 [ordered]@{exe=$phase4Build.exe;exe_sha256=$phase4Build.exe_sha256;arguments=$phase4Args;requested_skill=$phase4Case.skill;requested_enemies=$phase4Case.count;source_manifest_path=$phase4Build.source_manifest;source_manifest_sha256=(Get-FileHash -LiteralPath $phase4Build.source_manifest).Hash.ToLower();embedded_preexport_manifest_sha256=$phase4Build.metadata_sha256;start_utc=[DateTime]::UtcNow.ToString('o');scope='Ordinary exported Baseline scene with built-in QA aiming and enemy AI disabled; not native user input or performance evidence'}|ConvertTo-Json -Depth 4|Set-Content -Encoding utf8 -LiteralPath (Join-Path $phase4Directory 'launch.json')
 $phase4Process=Start-Process -FilePath $phase4Build.exe -ArgumentList $phase4Args -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $phase4Directory 'stdout.log') -RedirectStandardError (Join-Path $phase4Directory 'stderr.log')
 if(-not $phase4Process.WaitForExit(30000)){if($phase4Process.Path -eq $phase4Build.exe){$phase4Process.Kill()};throw 'Owned QA case timed out'}
 $phase4Process.WaitForExit()
 $phase4Results+=[pscustomobject]@{name=$phase4Case.name;actual_exit=$phase4Process.ExitCode;stderr_bytes=(Get-Item -LiteralPath (Join-Path $phase4Directory 'stderr.log')).Length;report_exists=(Test-Path -LiteralPath (Join-Path $phase4Directory 'scene-run.json'));frame_exists=(Test-Path -LiteralPath $phase4Frame);exe_sha256=(Get-FileHash -LiteralPath $phase4Build.exe).Hash.ToLower()}
 $phase4Results|ConvertTo-Json -Depth 4|Set-Content -Encoding utf8 -LiteralPath (Join-Path $Output 'qa-receipts.json')
}
$phase4Changed=@()
foreach($phase4File in $phase4Source.Keys){if((Get-FileHash -LiteralPath (Join-Path $ProjectRoot $phase4File)).Hash.ToLower() -ne $phase4Source[$phase4File]){$phase4Changed+=$phase4File}}
[ordered]@{source_count=$phase4Source.Count;source_mismatches=$phase4Changed;game_processes_remaining=@(Get-CimInstance Win32_Process|Where-Object{$_.Name -match '^(Godot|D2RCombatBaseline)'}).Count}|ConvertTo-Json|Set-Content -Encoding utf8 -LiteralPath (Join-Path $Output 'post-qa-preservation.json')
$phase4Results|ConvertTo-Json -Depth 4
if($phase4Results.Where({$_.actual_exit -ne 0 -or $_.stderr_bytes -ne 0 -or -not $_.report_exists -or -not $_.frame_exists -or $_.exe_sha256 -ne $phase4Build.exe_sha256}).Count -gt 0 -or $phase4Changed.Count -gt 0){exit 1}
exit 0
