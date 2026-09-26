#!/usr/bin/env bash
set -euo pipefail
rm -rf public /tmp/yc-preview /tmp/yc-preview.zip
mkdir -p public /tmp/yc-preview
cat \
  your-clinic-public/part00.txt \
  your-clinic-public/part01.txt \
  your-clinic-public/part-missing.txt \
  your-clinic-public/part02.txt \
  your-clinic-public/part-tail.txt \
  | base64 -d > /tmp/yc-preview.zip
python3 - <<'PY'
import zipfile
with zipfile.ZipFile('/tmp/yc-preview.zip') as z:
    z.extractall('/tmp/yc-preview')
PY
cp -R /tmp/yc-preview/Your-Clinic-Live-Preview/. public/
test -s public/index.html
printf 'Your Clinic preview built successfully\n'
