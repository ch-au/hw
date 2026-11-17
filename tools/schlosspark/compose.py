import sys
from PIL import Image, ImageDraw
T='out/theme/'; m=Image.open('out/map/map.png')
W,H=m.size
bg=Image.new('RGBA',(W,H),(0x3F,0x7F,0xD6,255))
sky=Image.open(T+'Sky.png'); hz=Image.open(T+'horizont.png'); hl=Image.open(T+'horizontL.png')
for x in range(0,W,sky.width): bg.alpha_composite(sky,(x,H-sky.height-250))
cx=(W-hz.width)//2; y=H-hz.height-60
bg.alpha_composite(hz,(cx,y))
x=cx-hl.width
while x>-hl.width: bg.alpha_composite(hl,(x,y)); x-=hl.width
x=cx+hz.width
while x<W: bg.alpha_composite(hl,(x,y)); x+=hl.width
cl=Image.open(T+'Clouds.png')
for i,(px,py) in enumerate([(300,250),(1300,120),(2300,330),(3500,180)]):
    bg.alpha_composite(cl.crop((0,128*i,256,128*i+128)).resize((512,256)),(px,py))
bg.alpha_composite(m)
ov=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(ov); d.rectangle((0,H-110,W,H),fill=(70,110,150,200))
bg.alpha_composite(ov)
bg=bg.convert('RGB')
bg.resize((2048,1024),Image.LANCZOS).save(sys.argv[1])
bg.crop((1400,900,3448,1948)).save(sys.argv[2])
