#!/usr/bin/env bash
# Скачивает все отчёты из data/sources_inventory.json в папку sources/.
# Запуск (из корня репозитория):  bash scripts/fetch_sources.sh
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INV="$ROOT/data/sources_inventory.json"
DEST="$ROOT/sources"
mkdir -p "$DEST"
ok=0; skip=0; fail=0
# требует python3 для разбора JSON
python3 - "$INV" <<'PY' | while IFS=$'\t' read -r name url; do
import json,sys
d=json.load(open(sys.argv[1],encoding="utf-8"))
for f in d["files"]:
    print(f["file"]+"\t"+(f.get("source_url") or ""))
PY
  out="$DEST/$name"
  if [ -f "$out" ]; then echo "SKIP  $name"; skip=$((skip+1)); continue; fi
  if [ -z "$url" ]; then echo "NOURL $name"; fail=$((fail+1)); continue; fi
  if curl -sL --fail -A "Mozilla/5.0" --max-time 300 "$url" -o "$out"; then
    echo "OK    $name"; ok=$((ok+1))
  else
    rm -f "$out"; echo "FAIL  $name"; fail=$((fail+1))
  fi
done
echo "Готово: OK=$ok SKIP=$skip FAIL=$fail"
