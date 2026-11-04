param([string]$BuildId = ('phase6-' + [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss')))
$ErrorActionPreference = 'Stop'
if ($BuildId -notmatch '^phase6-[a-zA-Z0-9-]+$') { throw 'Invalid build id' }
$taskRoot = 'C:\Project\d2r-combat-baseline'
$taskEngine = 'C:\Project\rea-tools\godot-4.5.1\Godot_v4.5.1-stable_win64_console.exe'
$taskOut = Join-Path $taskRoot ('builds\phase6\' + $BuildId)
$taskEvidence = Join-Path $taskRoot ('evidence\phase6\builds\' + $BuildId)
if ((Test-Path -LiteralPath $taskOut) -or (Test-Path -LiteralPath $taskEvidence)) { throw 'Preserve existing build/evidence; choose a new build id' }
New-Item -ItemType Directory -Path $taskOut,$taskEvidence | Out-Null
$taskPaths = @('baseline_sim.gd','baseline_view.gd','project.godot','Baseline.tscn','export_presets.cfg','game_data/catalog.json','data/game_catalog.gd','game_data/equipment.json','game_data/loot.json','benchmark/crowd_benchmark.gd','benchmark/crowd_benchmark.tscn','benchmark/flight_qa.gd','benchmark/flight_qa.tscn')
foreach ($taskFolder in @('combat','presentation','data')) {
 foreach ($taskFile in Get-ChildItem -LiteralPath (Join-Path $taskRoot $taskFolder) -Filter '*.gd' -File) { $taskPaths += ($taskFolder + '/' + $taskFile.Name) }
}
$taskHashes = [ordered]@{}
foreach ($taskPath in ($taskPaths | Sort-Object -Unique)) { $taskHashes[$taskPath] = (Get-FileHash -LiteralPath (Join-Path $taskRoot $taskPath) -Algorithm SHA256).Hash.ToLower() }
$taskInfoPath = Join-Path $taskRoot 'game_data/build_info.json'
Copy-Item -LiteralPath $taskInfoPath -Destination (Join-Path $taskEvidence 'previous-build_info.json')
[ordered]@{build_id=$BuildId;basis='pre-export source manifest; exported script remaps are not runtime original source bytes';source_hashes=$taskHashes} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $taskInfoPath -Encoding utf8
$taskManifest = [ordered]@{}
foreach ($taskPath in $taskHashes.Keys) { $taskManifest[$taskPath] = $taskHashes[$taskPath] }
$taskManifest['game_data/build_info.json'] = (Get-FileHash -LiteralPath $taskInfoPath).Hash.ToLower()
$taskSnapshot = Join-Path $taskEvidence 'source'
foreach ($taskPath in $taskManifest.Keys) {
 $taskTarget = Join-Path $taskSnapshot $taskPath
 New-Item -ItemType Directory -Path (Split-Path -Parent $taskTarget) -Force | Out-Null
 Copy-Item -LiteralPath (Join-Path $taskRoot $taskPath) -Destination $taskTarget
}
$taskManifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskEvidence 'source-manifest.json') -Encoding utf8
$taskExe = Join-Path $taskOut 'D2RCombatBaseline-phase6.exe'
& $taskEngine --headless --path $taskRoot --export-release 'Windows Desktop' $taskExe *> (Join-Path $taskEvidence 'export.log')
$taskExit = $LASTEXITCODE
if ($taskExit -ne 0 -or -not (Test-Path -LiteralPath $taskExe)) { throw ('Export failed: ' + $taskExit) }
foreach ($taskPath in $taskManifest.Keys) { if ((Get-FileHash -LiteralPath (Join-Path $taskRoot $taskPath)).Hash.ToLower() -ne $taskManifest[$taskPath]) { throw ('Source changed during export: ' + $taskPath) } }
[ordered]@{build_id=$BuildId;exe=$taskExe;exe_sha256=(Get-FileHash -LiteralPath $taskExe).Hash.ToLower();source_manifest=(Join-Path $taskEvidence 'source-manifest.json');source_count=$taskManifest.Count;export_exit=$taskExit;metadata_sha256=$taskManifest['game_data/build_info.json'];scope='Independent phase6 candidate; feature/performance/root acceptance are separate'} | ConvertTo-Json -Depth 5 | Tee-Object -FilePath (Join-Path $taskEvidence 'build.json')

