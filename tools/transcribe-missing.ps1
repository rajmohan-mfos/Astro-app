$px = "C:\Users\hgkri\workspace\Astro-app\tools\.venv-tx\Scripts\python.exe"
$tool = "C:\Users\hgkri\workspace\Astro-app\tools\transcribe.py"
$src = "C:\Users\hgkri\Downloads\yt-grab"
$out = "C:\Users\hgkri\workspace\Astro-app\backend\knowledge\transcripts"
foreach ($only in @("ASTRO CLASS 2", "CLASS- 3", "CLASS-7", "CLASS -10", "12 BHAVAM", "EXAMPLE CHART")) { & $px $tool $src --only $only --out $out }
