$ErrorActionPreference = 'Stop'
$managerUrl = 'http://127.0.0.1:8781/'
$managerRoot = Split-Path -Parent $PSCommandPath
function Test-ManagerReady {
    try {
        $catalog = Invoke-RestMethod ($managerUrl + 'api/catalog') -TimeoutSec 2
        return ($null -ne $catalog.schema_version -and $null -ne $catalog.entities)
    } catch { return $false }
}
if (-not (Test-ManagerReady)) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) { throw 'Python 3.10 이상이 필요합니다.' }
    Start-Process -FilePath $pythonCommand.Source -ArgumentList @('-B', ('"' + (Join-Path $managerRoot 'server.py') + '"'), '--port', '8781') -WorkingDirectory $managerRoot -WindowStyle Hidden
    for ($managerAttempt = 0; $managerAttempt -lt 20; $managerAttempt++) {
        if (Test-ManagerReady) { break }
        Start-Sleep -Milliseconds 250
    }
    if (-not (Test-ManagerReady)) { throw '제작실 서버를 열지 못했습니다. 8781 포트와 Python 설치를 확인하세요.' }
}
Start-Process $managerUrl
