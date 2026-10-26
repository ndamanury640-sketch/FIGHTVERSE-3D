import sys,glob,os
from playwright.sync_api import sync_playwright
src,dst=sys.argv[1],sys.argv[2]; os.makedirs(dst,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':800,'height':1000})
    for f in sorted(glob.glob(src+'/*.svg')):
        pg.goto('file://'+os.path.abspath(f)); pg.screenshot(path=os.path.join(dst,os.path.basename(f)[:-4]+'.png'))
    b.close()
