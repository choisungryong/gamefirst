param([string]$BuildId = ('phase7-' + [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss')), [switch]$Export, [switch]$ResumePrepared)
$ErrorActionPreference = 'Stop'
$taskPython = 'C:\Users\twins\AppData\Local\Programs\Python\Python310\python.exe'
$taskArgs = @('C:\Project\d2r-combat-baseline\tools\build_phase7.py','--build-id',$BuildId)
if ($Export) { $taskArgs += '--export' }
if ($ResumePrepared) { $taskArgs += '--resume-prepared' }
& $taskPython @taskArgs
if ($LASTEXITCODE -ne 0) { throw ('Phase7 staging/export failed: ' + $LASTEXITCODE) }
