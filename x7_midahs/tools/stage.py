#!/usr/bin/env python3
"""Stage this app only. Never create or overwrite shared volume/config files."""
from pathlib import Path
import shutil
import sys
app, desktop, destination = map(Path, sys.argv[1:])
(destination/'apps').mkdir(parents=True, exist_ok=True)
(destination/'res/midahs').mkdir(parents=True, exist_ok=True)
shutil.copy2(app, destination/'apps/midahs.app')
shutil.copy2(desktop, destination/'apps/midahs.desktop')
print(f'Card files: {destination}')

resource = Path(__file__).resolve().parents[1]/'resources/panel.rgb565'
shutil.copy2(resource, destination/'res/midahs/panel.rgb565')
