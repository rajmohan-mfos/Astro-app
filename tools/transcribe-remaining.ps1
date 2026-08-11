# Transcribes the remaining GRAHA MARKETS videos one by one.
# Launched detached so it survives Claude Code / terminal restarts.
# Progress log: backend\knowledge\transcripts\transcribe.log
$px = "C:\Users\hgkri\workspace\Astro-app\tools\.venv-tx\Scripts\python.exe"
$tool = "C:\Users\hgkri\workspace\Astro-app\tools\transcribe.py"
$src = "C:\Users\hgkri\Downloads\yt-grab"
$out = "C:\Users\hgkri\workspace\Astro-app\backend\knowledge\transcripts"
$log = Join-Path $out "transcribe.log"

$targets = @(
    "LONG TERM INVESTMENT", "CLASS - 11", "PRASANAM VIDEO 1", "prasanam 2",
    "CLASS -4", "CLASS -6", "CLASS -8", "CLASS -9",
    "ASTRO CLASS 2", "CLASS- 3", "CLASS-7", "CLASS -10",
    "12 BHAVAM", "EXAMPLE CHART"
)

Add-Content $log "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] batch start ($($targets.Count) targets)"
foreach ($only in $targets) {
    Add-Content $log "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] starting: $only"
    & $px $tool $src --only $only --out $out 2>&1 | Add-Content $log
}
Add-Content $log "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ALL DONE"
