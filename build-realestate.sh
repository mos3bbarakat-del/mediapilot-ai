#!/usr/bin/env bash
set -euo pipefail
rm -rf realestate-fullstack realestate-fullstack.tar.gz fullstack.b64
cat realestate-b64/00 realestate-b64/01 realestate-b64/02 realestate-b64/03 realestate-b64/04 realestate-b64/05 realestate-b64/06 realestate-b64/07 realestate-b64/08 realestate-b64/09 realestate-b64/10 realestate-b64/11 > fullstack.b64
base64 -d fullstack.b64 > realestate-fullstack.tar.gz
echo "358c2feb63df39e4f1bc8ae4375229b3c1ae1158b4c4a189d0a55c31cb14f2a1  realestate-fullstack.tar.gz" | sha256sum -c -
tar -xzf realestate-fullstack.tar.gz
node --check realestate-fullstack/server.js
node --check realestate-fullstack/public/app.js
