param([string]$OutputRoot='C:\Project\d2r-combat-baseline\evidence\phase3\final-exe-qa-20261028')
$ErrorActionPreference='Stop'
if(Test-Path -LiteralPath $OutputRoot){throw 'Preserve prior QA evidence; choose a new root'}
New-Item -ItemType Directory -Path $OutputRoot|Out-Null
$taskExe='C:\Project\d2r-combat-baseline\builds\phase3\D2RCombatBaseline-phase3.exe'
$taskPin='76BBB630424B7A2F2D65C6587C781ADDEC58D6A1C63D39C59396316A9D2CBFAD'
$taskCases=@()
foreach($taskCount in @(0,1,10,100)){$taskCases+=[pscustomobject]@{name=('normal-qa-n'+$taskCount);count=$taskCount;flight=$false}}
$taskCases+=[pscustomobject]@{name='exported-flight-qa';count=0;flight=$true}
$taskResults=@()
foreach($taskCase in $taskCases){
 if((Get-FileHash -LiteralPath $taskExe).Hash -ne $taskPin){throw 'Final EXE changed'}
 $taskOut=Join-Path $OutputRoot $taskCase.name
 New-Item -ItemType Directory -Path $taskOut|Out-Null
 $taskUnix=$taskOut.Replace('\','/')
 $taskArgs=@('--windowed','--resolution','1920x1080','--rendering-method','forward_plus','--rendering-driver','vulkan')
 if($taskCase.flight){$taskArgs+=@('--scene','res://benchmark/flight_qa.tscn','--',('--flight-output='+$taskUnix))}
 else{$taskArgs+=@('--','--qa',('--enemies='+$taskCase.count),('--capture='+$taskUnix+'/frame.png'),'--capture-at=1.15','--quit-after=3',('--report='+$taskUnix))}
 [ordered]@{exe=$taskExe;exe_sha256=$taskPin;arguments=$taskArgs;started_utc=[DateTime]::UtcNow.ToString('o');scope='Final standalone EXE functional QA; no performance claim'}|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $taskOut 'launch.json') -Encoding utf8
 $taskProcess=Start-Process -FilePath $taskExe -ArgumentList $taskArgs -WindowStyle Normal -PassThru -RedirectStandardOutput (Join-Path $taskOut 'stdout.log') -RedirectStandardError (Join-Path $taskOut 'stderr.log')
 if(-not $taskProcess.WaitForExit(60000)){if($taskProcess.Path -eq $taskExe){$taskProcess.Kill()};throw ('Owned QA timed out: '+$taskCase.name)}
 $taskProcess.WaitForExit()
 $taskExit=$taskProcess.ExitCode
 if($taskExit -ne 0){throw ('QA process failed '+$taskCase.name+' / '+$taskExit)}
 if((Get-Item -LiteralPath (Join-Path $taskOut 'stderr.log')).Length -ne 0){throw ('QA emitted stderr: '+$taskCase.name)}
 if($taskCase.flight){
  $taskReport=Get-Content -LiteralPath (Join-Path $taskOut 'flight-qa.json') -Raw|ConvertFrom-Json
  if(-not $taskReport.success -or $taskReport.maximum_bolts -ne 4 -or $taskReport.maximum_sprites -ne 4 -or -not $taskReport.capture_saved -or $taskReport.framebuffer_width -ne 1920 -or $taskReport.framebuffer_height -ne 1080){throw 'Exported flight QA did not prove its declared functional case'}
  $taskResult=[pscustomobject]@{name=$taskCase.name;exit=$taskExit;success=$taskReport.success;maximum_bolts=$taskReport.maximum_bolts;maximum_sprite_bindings=$taskReport.maximum_sprites;atlas_frames=$taskReport.atlas_frames.Count;paused=$taskReport.paused_bolts_atlas_particles_unchanged;reset_clean=$taskReport.reset_clears_bindings_hides_pools;width=$taskReport.framebuffer_width;height=$taskReport.framebuffer_height;scope='Four logical bolts/bindings, not four simultaneously visible bolts or performance'}
 }else{
  $taskReport=Get-Content -LiteralPath (Join-Path $taskOut 'scene-run.json') -Raw|ConvertFrom-Json
  if($taskReport.requested_enemies -ne $taskCase.count -or $taskReport.entities -ne $taskCase.count -or $taskReport.actor_count -ne $taskCase.count -or -not $taskReport.capture_saved -or $taskReport.framebuffer_width -ne 1920 -or $taskReport.framebuffer_height -ne 1080){throw ('Normal QA count/capture contract failed '+$taskCase.name)}
  if($taskCase.count -eq 0 -and ($taskReport.shots -ne 0 -or $taskReport.hits -ne 0)){throw 'Zero enemy QA leaked casts'}
  if($taskCase.count -eq 1 -and ($taskReport.shots -ne 3 -or $taskReport.hits -ne 2 -or $taskReport.mana_raw -ne 7040 -or $taskReport.enemy_state -ne 'dead')){throw 'Single enemy baseline regression in final EXE'}
  $taskResult=[pscustomobject]@{name=$taskCase.name;exit=$taskExit;requested=$taskReport.requested_enemies;entities=$taskReport.entities;actors=$taskReport.actor_count;alive=$taskReport.alive;shots=$taskReport.shots;hits=$taskReport.hits;mana_raw=$taskReport.mana_raw;width=$taskReport.framebuffer_width;height=$taskReport.framebuffer_height;capture_saved=$taskReport.capture_saved;scope='Actual final EXE automated functional QA, no performance claim'}
 }
 $taskResults+=$taskResult
 $taskResults|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $OutputRoot 'qa-results.json') -Encoding utf8
 Write-Output ($taskResult|ConvertTo-Json -Compress)
}
if((Get-FileHash -LiteralPath $taskExe).Hash -ne $taskPin){throw 'Final EXE changed after QA'}
exit 0
