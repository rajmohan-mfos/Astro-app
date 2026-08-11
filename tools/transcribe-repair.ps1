$px = "C:\Users\hgkri\workspace\Astro-app\tools\.venv-tx\Scripts\python.exe"
$tool = "C:\Users\hgkri\workspace\Astro-app\tools\transcribe.py"
$src = "C:\Users\hgkri\Downloads\yt-grab"
$out = "C:\Users\hgkri\workspace\Astro-app\backend\knowledge\transcripts"
while (Get-CimInstance Win32_Process -Filter "Name like 'python%'" | Where-Object { $_.CommandLine -match 'transcribe\.py' }) { Start-Sleep 60 }
foreach ($only in @("LONG TERM INVESTMENT", "PRASANAM VIDEO 1")) { & $px $tool $src --only $only --out $out }
