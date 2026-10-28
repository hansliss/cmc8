#!/usr/bin/env python3
"""Stage this app only. Never create or overwrite shared volume/config files."""
from pathlib import Path
import shutil
import sys
app, desktop, destination = map(Path, sys.argv[1:])
(destination/'apps').mkdir(parents=True, exist_ok=True)
(destination/'res/cmc8-traffic').mkdir(parents=True, exist_ok=True)
shutil.copy2(app, destination/'apps/cmc8-traffic.app')
shutil.copy2(desktop, destination/'apps/cmc8-traffic.desktop')
print(f'Card files: {destination}')
