#!/bin/zsh
# Rebuild the page from the CSVs, then print it to Save91_SWOT_and_Competitors.pdf (A4 landscape).
cd "${0:A:h}"
python3 build_swot.py || exit 1
{ sed -e 's/<details/<details open/g' swot_offline.html; echo "<style>"; cat print.css; echo "</style>"; } > .print.html
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --no-pdf-header-footer \
  --virtual-time-budget=8000 --print-to-pdf="$PWD/Save91_SWOT_and_Competitors.pdf" "file://$PWD/.print.html" 2>/dev/null
rm -f .print.html
python3 -c "import re;d=open('Save91_SWOT_and_Competitors.pdf','rb').read();print('pdf pages',len(re.findall(rb'/Type\s*/Page[^s]',d)))"
