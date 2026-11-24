# PowerShell 7 or Windows PowerShell 5.1. Uses only a new temporary directory.
$ErrorActionPreference = 'Stop'
$working = Join-Path ([IO.Path]::GetTempPath()) ('bulletin-restore-' + [guid]::NewGuid())
$null = New-Item -ItemType Directory -Path $working
$document = Join-Path $working 'bulletin.txt'
$archive = Join-Path $working 'bulletin.zip'
try {
    Set-Content -LiteralPath $document -Value 'News bulletin approved for the morning shift.'
    $approved = (Get-FileHash -LiteralPath $document -Algorithm SHA256).Hash
    Compress-Archive -LiteralPath $document -DestinationPath $archive
    Set-Content -LiteralPath $document -Value 'Incomplete replacement copy.'
    $incorrect = (Get-FileHash -LiteralPath $document -Algorithm SHA256).Hash
    if ($approved -eq $incorrect) { throw 'Fault injection did not change the file.' }
    $recovery = Join-Path $working 'restore'
    Expand-Archive -LiteralPath $archive -DestinationPath $recovery
    $candidate = Join-Path $recovery 'bulletin.txt'
    if ((Get-FileHash -LiteralPath $candidate -Algorithm SHA256).Hash -ne $approved) {
        throw 'Restored archive failed verification. Original held for review.'
    }
    Copy-Item -LiteralPath $candidate -Destination $document -Force
    $restored = (Get-FileHash -LiteralPath $document -Algorithm SHA256).Hash
    if ($restored -ne $approved) { throw 'Final verification failed.' }
    [pscustomobject]@{ case = 'Windows file recovery'; platform = [Environment]::OSVersion.VersionString;
        powershell = $PSVersionTable.PSVersion.ToString(); expected = $approved; affected = $incorrect;
        recovered = $restored; status = 'PASS' } | ConvertTo-Json
} finally {
    Remove-Item -LiteralPath $working -Recurse -Force
}
