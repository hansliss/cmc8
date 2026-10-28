#!/usr/bin/env python3
"""Optional asset preparation; Pillow is needed only to regenerate the RGB565 photo."""
from pathlib import Path
import sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
image=Image.open(ROOT/'resources/panel-source.jpg').convert('RGB')
if image.size!=(391,272):raise SystemExit('Expected the supplied 391x272 corrected photo')
output=bytearray()
for r,g,b in image.getdata():
    output.extend((((r>>3)<<11)|((g>>2)<<5)|(b>>3)).to_bytes(2,'little'))
path=ROOT/'resources/panel.rgb565'
if '--check' in sys.argv:
    if path.read_bytes()!=output:raise SystemExit('Stale panel.rgb565')
    print('RGB565 photo matches the corrected source image')
else:path.write_bytes(output)
