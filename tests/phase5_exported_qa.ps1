param(
 [string]$ProjectRoot='C:\Project\d2r-combat-baseline',
 [string]$BuildRecord='C:\Project\d2r-combat-baseline\evidence\phase5\builds\phase5-candidate-20261029-01\build.json',
 [string]$Output='C:\Project\d2r-combat-baseline\evidence\phase5\final-exe-equipment-qa-20261030-02'
)
$ErrorActionPreference='Stop'
if(Test-Path -LiteralPath $Output){throw 'Preserve prior QA output'}
$qaBuild=Get-Content -Raw -LiteralPath $BuildRecord|ConvertFrom-Json
$qaManifest=Get-Content -Raw -LiteralPath $qaBuild.source_manifest|ConvertFrom-Json -AsHashtable
$qaScript=Join-Path $ProjectRoot 'tests\phase5_exported_qa.gd'
$qaScriptHash=(Get-FileHash -LiteralPath $qaScript).Hash.ToLower()
foreach($qaFile in $qaManifest.Keys){if((Get-FileHash -LiteralPath (Join-Path $ProjectRoot $qaFile)).Hash.ToLower() -ne $qaManifest[$qaFile]){throw ('Changed product: '+$qaFile)}}
if((Get-FileHash -LiteralPath $qaBuild.exe).Hash.ToLower() -ne $qaBuild.exe_sha256){throw 'Changed executable'}
if(@(Get-CimInstance Win32_Process|Where-Object{$_.Name -match '^(Godot|D2RCombatBaseline)'}).Count){throw 'Another GPU owner'}
New-Item -ItemType Directory -Path $Output|Out-Null
$qaReceipts=@()
foreach($qaSize in @(@(1440,810),@(1920,1080))){
 $qaCase=Join-Path $Output ($qaSize[0].ToString()+'x'+$qaSize[1])
 $qaArgs=@('--windowed','--resolution',($qaSize[0].ToString()+'x'+$qaSize[1]),'--rendering-method','forward_plus','--rendering-driver','vulkan','--script',$qaScript,'--','--enemies=0',('--qa-output='+$qaCase.Replace('\','/')),('--expected-metadata='+$qaBuild.metadata_sha256),('--qa-width='+$qaSize[0]),('--qa-height='+$qaSize[1]))
 [ordered]@{exe=$qaBuild.exe;exe_sha256=$qaBuild.exe_sha256;build_record=$BuildRecord;metadata_sha256=$qaBuild.metadata_sha256;source_manifest=$qaBuild.source_manifest;external_script=$qaScript;external_script_sha256=$qaScriptHash;arguments=$qaArgs;start_utc=[DateTime]::UtcNow.ToString('o')}|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $Output ($qaSize[0].ToString()+'x'+$qaSize[1]+'-launch.json')) -Encoding utf8
 $qaStdout=Join-Path $Output ($qaSize[0].ToString()+'x'+$qaSize[1]+'.stdout.log')
 $qaStderr=Join-Path $Output ($qaSize[0].ToString()+'x'+$qaSize[1]+'.stderr.log')
 $qaProcess=Start-Process -FilePath $qaBuild.exe -ArgumentList $qaArgs -WorkingDirectory (Split-Path -Parent $qaBuild.exe) -WindowStyle Hidden -PassThru -RedirectStandardOutput $qaStdout -RedirectStandardError $qaStderr
 if(-not $qaProcess.WaitForExit(45000)){if($qaProcess.Path -eq $qaBuild.exe){$qaProcess.Kill()};throw 'Owned external QA deadline exceeded'}
 $qaProcess.WaitForExit()
 $qaReportPath=Join-Path $qaCase 'qa-report.json'
 $qaReport=if(Test-Path -LiteralPath $qaReportPath){Get-Content -Raw -LiteralPath $qaReportPath|ConvertFrom-Json}else{$null}
 $qaReceipt=[ordered]@{dimensions=$qaSize;actual_exit=$qaProcess.ExitCode;report_path=$qaReportPath;report_success=($null -ne $qaReport -and $qaReport.success);checks=if($qaReport){$qaReport.checks}else{0};failures=if($qaReport){$qaReport.failures}else{@('Missing report')};stderr_bytes=(Get-Item -LiteralPath $qaStderr).Length;script_hash_matches=($null -ne $qaReport -and $qaReport.external_script_sha256 -eq $qaScriptHash);metadata_matches=($null -ne $qaReport -and $qaReport.metadata_sha256 -eq $qaBuild.metadata_sha256)}
 $qaReceipts += [pscustomobject]$qaReceipt
 $qaReceipts|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $Output 'qa-receipts.json') -Encoding utf8
 $qaReceipt|ConvertTo-Json -Depth 4 -Compress|Write-Output
 if($qaProcess.ExitCode -ne 0 -or -not $qaReceipt.report_success -or -not $qaReceipt.script_hash_matches -or -not $qaReceipt.metadata_matches){exit 1}
}
$qaMismatches=@()
foreach($qaFile in $qaManifest.Keys){if((Get-FileHash -LiteralPath (Join-Path $ProjectRoot $qaFile)).Hash.ToLower() -ne $qaManifest[$qaFile]){$qaMismatches+=$qaFile}}
$qaRemaining=@(Get-CimInstance Win32_Process|Where-Object{$_.Name -match '^(Godot|D2RCombatBaseline)'})
[ordered]@{source_count=$qaManifest.Count;source_mismatches=$qaMismatches;game_processes_remaining=$qaRemaining.Count;exe_sha256=(Get-FileHash -LiteralPath $qaBuild.exe).Hash.ToLower()}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $Output 'post-qa-preservation.json') -Encoding utf8
if($qaMismatches.Count -or $qaRemaining.Count){exit 1}
exit 0
