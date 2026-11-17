import sys
from PIL import Image, ImageDraw
T='out/photo/theme/'
def mock(name, out):
    m=Image.open(f'out/photo/{name}/map.png'); W,H=m.size
    bg=Image.new('RGBA',(W,H),(92,148,224,255))
    sky=Image.open(T+'Sky.png'); hz=Image.open(T+'horizont.png')
    for x in range(0,W,sky.width): bg.alpha_composite(sky,(x,H-sky.height-200))
    x=-(hz.width-W)//2
    bg.alpha_composite(hz,(x,H-hz.height-40))
    cl=Image.open(T+'Clouds.png')
    for i,(px,py) in enumerate([(200,200),(1100,90),(2000,260),(2900,150)]):
        if px<W: bg.alpha_composite(cl.crop((0,128*i,256,128*i+128)).resize((512,256)),(px,py))
    bg.alpha_composite(m)
    ov=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(ov); d.rectangle((0,H-100,W,H),fill=(60,95,130,210)); bg.alpha_composite(ov)
    bg=bg.convert('RGB'); bg.resize((W//2,H//2),Image.LANCZOS).save(out)
mock('Schloss','out/mock_schloss.png'); mock('Hochhaus','out/mock_hochhaus.png')
