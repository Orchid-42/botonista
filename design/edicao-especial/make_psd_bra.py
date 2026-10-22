"""Brasil 1970 special edition: artboards by game position (1 = goalkeeper card), shirt numbers baked in with the
1970 kit numerals, CBD crest top-right with the number below it (like the reference), green trim on yellow."""
import sys
sys.path.insert(0,'/tmp/claude-0/-home-claude/aaf3b37c-e613-5240-8f46-8d80e127a663/scratchpad')
from psdlib import *
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FONT_B='/usr/share/fonts/opentype/inter/Inter-Bold.otf'; FONT_R='/usr/share/fonts/opentype/inter/Inter-Regular.otf'
MAP={1:1,2:4,3:3,4:2,5:8,6:16,7:11,8:5,9:10,10:9,11:7}
GREEN=(0,128,55,255);YELLOW=(245,191,11,255)
a=np.array(Image.open('/tmp/claude-0/bra/font.png').convert('RGB')).astype(float)
# glyph coverage: how far each pixel is from the yellow paper toward the dark green ink
ink=np.clip((a[:,:,0]-30)/(245-30),0,1);cov=1-ink
SEG=[[(14,63),(76,103),(116,165),(178,234),(247,305)],[(14,69),(75,129),(136,189),(196,247),(254,306)]];ROWS=[(11,86),(126,202)]
G={}
for r,(y0,y1) in enumerate(ROWS):
    for k,(x0,x1) in enumerate(SEG[r]):
        m=Image.fromarray((cov[y0:y1,x0:x1]*255).astype('uint8'));G[str(r*5+k)]=m
GH=75
def number(n,h):
    s=str(n);k=h/GH;gap=int(GH*.09*k);gs=[]
    for c in s:
        g=G[c];w=max(1,int(g.width*k));big=g.resize((w*4,int(h)*4),Image.BICUBIC).filter(ImageFilter.GaussianBlur(2))
        arr=np.array(big).astype(float)/255;arr=np.clip((arr-.35)/.3,0,1)  # re-sharpen the upscaled edge
        gs.append(Image.fromarray((arr*255).astype('uint8')).resize((w,int(h)),Image.LANCZOS))
    W=sum(g.width for g in gs)+gap*(len(gs)-1);out=Image.new('L',(W,int(h)),0);x=0
    for g in gs:out.paste(g,(x,0));x+=g.width+gap
    return out
logo=Image.open('/tmp/claude-0/bra/logo_t.png').convert('RGBA');logo=logo.crop(logo.getbbox())
def fit_logo(h):return logo.resize((int(logo.width*h/logo.height),int(h)),Image.LANCZOS)
BS=1024;KW,KH=1960,680;GAP=160;SSx=2
def blank(w,h):return Image.new('RGBA',(w,h),(0,0,0,0))
def btn_layers(num):
    S=BS*SSx;c=S/2
    bg=blank(S,S);d=ImageDraw.Draw(bg);r=c*.985;d.ellipse((c-r,c-r,c+r,c+r),fill=YELLOW);bg=bg.resize((BS,BS),Image.LANCZOS)
    tr=blank(S,S);d=ImageDraw.Draw(tr);w=c*.105;d.ellipse((c-r,c-r,c+r,c+r),outline=GREEN,width=int(w));tr=tr.resize((BS,BS),Image.LANCZOS)
    # crest high on the right, number lower on the right (as in the reference)
    lh=int(BS*.215);lg=fit_logo(lh);crest=blank(BS,BS);cx=int(BS*.645);crest.alpha_composite(lg,(cx-lg.width//2,int(BS*.205)))
    nh=int(BS*.17);nm=number(num,nh);numL=blank(BS,BS);col=Image.new('RGBA',nm.size,GREEN);col.putalpha(nm);nx=int(BS*.665)
    numL.alpha_composite(col,(nx-nm.width//2,int(BS*.565)))
    return bg,tr,crest,numL
def btn_guides(pos,num):
    L=[];im=blank(BS,BS);d=ImageDraw.Draw(im);c=BS/2;r=c*.97
    d.ellipse((c-r,c-r,c+r,c+r),outline=(255,0,170,255),width=5);L.append(('Visible face (glass edge)',im))
    im=blank(BS,BS);d=ImageDraw.Draw(im);x0,x1,y0,y1=int(BS*.14),int(BS*.56),int(BS*.14),int(BS*.92)
    for x in range(x0,x1,24):d.line((x,y0,x+12,y0),fill=(0,190,255,255),width=4);d.line((x,y1,x+12,y1),fill=(0,190,255,255),width=4)
    for y in range(y0,y1,24):d.line((x0,y,x0,y+12),fill=(0,190,255,255),width=4);d.line((x1,y,x1,y+12),fill=(0,190,255,255),width=4)
    fr=ImageFont.truetype(FONT_R,24);d.text(((x0+x1)//2,(y0+y1)//2),'foto',font=fr,fill=(0,190,255,255),anchor='mm');L.append(('Photo area',im))
    im=blank(BS,BS);d=ImageDraw.Draw(im);fb=ImageFont.truetype(FONT_B,38)
    d.text((34,26),f"Posição {pos}  ·  camisa {num}",font=fb,fill=(255,255,255,255),stroke_width=5,stroke_fill=(17,24,34,255));L.append(('Notes',im))
    return L
def gk_layers(num):
    bg=Image.new('RGBA',(KW,KH),YELLOW);tr=blank(KW,KH);d=ImageDraw.Draw(tr);w=int(KH*.075);d.rectangle((0,0,KW-1,KH-1),outline=GREEN,width=w)
    lh=int(KH*.40);nh=int(KH*.30);gap=int(KH*.05);top=(KH-(lh+gap+nh))//2;cx=int(KW*.80)
    lg=fit_logo(lh);crest=blank(KW,KH);crest.alpha_composite(lg,(cx-lg.width//2,top))
    nm=number(num,nh);numL=blank(KW,KH);col=Image.new('RGBA',nm.size,GREEN);col.putalpha(nm);numL.alpha_composite(col,(cx-nm.width//2,top+lh+gap))
    return bg,tr,crest,numL
def gk_guides(num):
    L=[];im=blank(KW,KH);d=ImageDraw.Draw(im);x0,x1,y0,y1=int(KH*.12),int(KW*.66),int(KH*.12),int(KH*.88)
    for x in range(x0,x1,30):d.line((x,y0,x+15,y0),fill=(0,190,255,255),width=4);d.line((x,y1,x+15,y1),fill=(0,190,255,255),width=4)
    for y in range(y0,y1,30):d.line((x0,y,x0,y+15),fill=(0,190,255,255),width=4);d.line((x1,y,x1,y+15),fill=(0,190,255,255),width=4)
    fr=ImageFont.truetype(FONT_R,30);d.text(((x0+x1)//2,(y0+y1)//2),'foto',font=fr,fill=(0,190,255,255),anchor='mm');L.append(('Photo area',im))
    im=blank(KW,KH);d=ImageDraw.Draw(im);fb=ImageFont.truetype(FONT_B,40)
    d.text((70,60),f"Posição 1 (goleiro)  ·  camisa {num}",font=fb,fill=(40,40,40,255));L.append(('Notes',im));return L
W=5*BS+6*GAP;H=GAP*4+BS*2+KH;BG=(238,241,240)
comp=Image.new('RGBA',(W,H),(214,219,216,255));recs=[]
spots=[(p,GAP+i*(BS+GAP),GAP) for i,p in enumerate(range(2,7))]+[(p,GAP+i*(BS+GAP),GAP*3+BS+KH) for i,p in enumerate(range(7,12))]
def board(name,lay,g,off,w,h,num):
    bg,tr,cr,nm=lay;bd=Image.new('RGBA',(w,h),BG+(255,))
    for im in (bg,tr,cr,nm)+tuple(x[1] for x in g):bd.alpha_composite(im)
    comp.alpha_composite(bd,off)
    guide=group('Guides (hide before export)',[Layer(n,im,off) for n,im in reversed(g)])
    return group(name,[guide,Layer(f'Número {num}',nm,off),Layer('Escudo CBD',cr,off),Layer('Trim (verde)',tr,off),Layer('Foto (coloque aqui)',None),Layer('Fundo (amarelo)',bg,off)],artboard=((off[0],off[1],off[0]+w,off[1]+h),BG))
for pos,ox,oy in spots:
    num=MAP[pos];recs+=board(str(pos),btn_layers(num),btn_guides(pos,num),(ox,oy),BS,BS,num)
kx=(W-KW)//2;ky=GAP*2+BS;recs+=board('1',gk_layers(MAP[1]),gk_guides(MAP[1]),(kx,ky),KW,KH,MAP[1])
li=struct.pack('>h',-len(recs))+b''.join(L.record() for L in recs)+b''.join(L.data() for L in recs)
if len(li)%2:li+=b'\0'
li=struct.pack('>I',len(li))+li;lmi=li+struct.pack('>I',0);lmi=struct.pack('>I',len(lmi))+lmi
out=b'8BPS'+struct.pack('>H',1)+b'\0'*6+struct.pack('>HIIHH',4,H,W,8,3)+struct.pack('>I',0)+struct.pack('>I',0)+lmi
counts=b'';datas=b''
for ch in comp.split():
    raw=ch.tobytes();rws=[packbits(raw[y*W:(y+1)*W]) for y in range(H)];counts+=struct.pack('>'+'H'*H,*[len(x) for x in rws]);datas+=b''.join(rws)
out+=struct.pack('>H',1)+counts+datas
open(sys.argv[1],'wb').write(out);comp.convert('RGB').resize((W//5,H//5),Image.LANCZOS).save(sys.argv[2])
print(len(out)//1024,'KB',len(recs))
