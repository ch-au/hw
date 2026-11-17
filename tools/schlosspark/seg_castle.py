import os
PHOTO_DIR = os.environ.get('PHOTO_DIR', '.')  # folder with the two reference photos
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
SRC=PHOTO_DIR + '/schloss.png'
img=Image.open(SRC); im=np.array(img).astype(np.float32)
H,W=im.shape[:2]; K=W/2000.0
r,g,b=im[...,0],im[...,1],im[...,2]
mx=im.max(-1); mn=im.min(-1); sat=(mx-mn)/np.maximum(mx,1)
skyish=((mx>140)&(sat<0.16))|((b>=r)&(mx>110)&(sat<0.25))
green=(g>r*1.02)&(g>=b)&(sat>0.12)
cand=skyish|green
lab,n=ndi.label(cand)
border=set(np.unique(np.concatenate([lab[0],lab[:,0],lab[:,-1]])))-{0}
bg=np.isin(lab,list(border))
fg=~bg
# roof polygons (display coords) forced to foreground
roofs=[[(718,572),(1205,563),(1238,598),(1272,556),(1300,600),(1130,760),(718,760)],
       [(543,132),(604,42),(616,42),(672,132)],
       [(466,198),(500,156),(537,198)],
       [(637,193),(672,156),(708,198)],
       [(952,488),(1000,428),(1048,488)],
       [(1405,715),(1462,712),(1495,712),(1520,692),(1560,742),(1598,766),(1622,838),(1866,924),(1882,940),(1405,940)]]
m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
for p in roofs: d.polygon([(x*K,y*K) for x,y in p],fill=255)
fg|=np.array(m)>0
bgp=[[(0,0),(330,0),(330,1062),(0,1062)],
     [(1622,700),(2000,700),(2000,1062),(1892,1062),(1884,940),(1866,922),(1622,836)]]
m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
for p in bgp: d.polygon([(x*K,y*K) for x,y in p],fill=255)
fg&=~(np.array(m)>0)
# everything below the balustrade top is ground: keep (fills topiary/lawn)
yb=int(1062*K)
fg[yb:,:]=True
# clean
fg=ndi.binary_opening(fg,iterations=2)
lab,n=ndi.label(fg); sizes=ndi.sum(fg,lab,range(1,n+1)); fg=lab==(np.argmax(sizes)+1)
fg=ndi.binary_fill_holes(fg)
fg=ndi.binary_erosion(fg,iterations=2)
np.save('out/castle_fg.npy',fg)
rgba=np.dstack([np.array(img),(fg*255).astype(np.uint8)])
Image.fromarray(rgba,'RGBA').save('out/castle_cut.png')
v=Image.new('RGBA',(W,H),(255,0,255,255)); v.alpha_composite(Image.fromarray(rgba,'RGBA'))
v.convert('RGB').resize((1400,960)).save('out/castle_cut_v.png')
