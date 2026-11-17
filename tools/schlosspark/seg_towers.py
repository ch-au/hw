import os
PHOTO_DIR = os.environ.get('PHOTO_DIR', '.')  # folder with the two reference photos
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
SRC=PHOTO_DIR + '/hochhaus.png'
img=Image.open(SRC); im=np.array(img).astype(np.float32)
r,g,b=im[...,0],im[...,1],im[...,2]
H,W=r.shape
bgc=(b>r+22)&(b>g+2)
lab,n=ndi.label(bgc)
top=set(np.unique(lab[0]))-{0}
bg=np.isin(lab,list(top))
fg=~bg
polys=[[(143,500),(190,485),(360,488),(384,515),(384,645),(143,645)],
 [(395,492),(470,490),(475,470),(555,467),(584,480),(584,640),(395,640)],
 [(584,458),(640,445),(700,445),(705,437),(752,433),(756,420),(842,418),(866,440),(868,640),(584,640)],
 [(905,545),(930,542),(935,514),(985,511),(990,485),(1050,465),(1115,470),(1140,465),(1175,489),(1230,494),(1235,514),(1282,514),(1322,527),(1322,630),(905,630)]]
m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
for p in polys: d.polygon(p,fill=255)
pm=np.array(m)>0
# inside polygons keep pixels unless clearly sky-blue
fg|=pm&~((b>r+45)&(b>g+15)&(im.max(-1)<200)&(np.arange(H)[:,None]<470))
fg[:390,:]=False
fg=ndi.binary_opening(fg,iterations=1)
lab,n=ndi.label(fg); sizes=ndi.sum(fg,lab,range(1,n+1)); fg=lab==(np.argmax(sizes)+1)
fg=ndi.binary_fill_holes(fg)
rgba=np.dstack([np.array(img),(fg*255).astype(np.uint8)])
Image.fromarray(rgba,'RGBA').save('out/towers_cut.png')
v=Image.new('RGBA',(W,H),(255,0,255,255)); v.alpha_composite(Image.fromarray(rgba,'RGBA'))
v.convert('RGB').save('out/towers_cut_v.png')
