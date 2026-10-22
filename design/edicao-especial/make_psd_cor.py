"""Corinthians special edition: artboards named by game position (1 = goalkeeper card, 2-11 buttons), each with the
shirt number baked in using the user's kit font, the crest above it on the right, black trim, white face."""
import sys,math
sys.path.insert(0,'/tmp/claude-0/-home-claude/aaf3b37c-e613-5240-8f46-8d80e127a663/scratchpad')
from psdlib import *
import numpy as np
from PIL import Image, ImageDraw, ImageFont
FONT_B='/usr/share/fonts/opentype/inter/Inter-Bold.otf'; FONT_R='/usr/share/fonts/opentype/inter/Inter-Regular.otf'
MAP={1:12,2:2,3:13,4:3,5:8,6:6,7:23,8:5,9:9,10:20,11:11}
# glyphs from the font sheet
f=Image.open('/tmp/claude-0/cor/font.png').convert('RGBA');a=np.array(f);dark=((a[:,:,:3].mean(2)<128)&(a[:,:,3]>128))
SEG=[(1,137),(171,251),(286,407),(429,553),(587,726),(763,884),(919,1055),(1074,1199),(1220,1356),(1386,1521)]
GH=266
G={}
for d,(x0,x1) in enumerate(SEG):
    m=Image.fromarray((dark[:GH,x0:x1]*255).astype('uint8'));G[str(d)]=m
def number(n,h):
    s=str(n);gs=[G[c] for c in s];k=h/GH;gap=int(GH*.07*k)
    ws=[max(1,int(g.width*k)) for g in gs];W=sum(ws)+gap*(len(gs)-1)
    out=Image.new('L',(W,int(h)),0);x=0
    for g,w in zip(gs,ws):out.paste(g.resize((w,int(h)),Image.LANCZOS),(x,0));x+=w+gap
    return out
logo=Image.open('/tmp/claude-0/cor/logo.png').convert('RGBA');logo=logo.crop(logo.getbbox())
def fit_logo(h):return logo.resize((int(logo.width*h/logo.height),int(h)),Image.LANCZOS)
BS=1024;KW,KH=1960,680;GAP=160;SSx=2
def blank(w,h):return Image.new('RGBA',(w,h),(0,0,0,0))
def btn_layers(num):
    S=BS*SSx;c=S/2
    bg=blank(S,S);d=ImageDraw.Draw(bg);r=c*.985;d.ellipse((c-r,c-r,c+r,c+r),fill=(255,255,255,255));bg=bg.resize((BS,BS),Image.LANCZOS)
    tr=blank(S,S);d=ImageDraw.Draw(tr);r=c*.985;w=c*.13;d.ellipse((c-r,c-r,c+r,c+r),outline=(0,0,0,255),width=int(w));tr=tr.resize((BS,BS),Image.LANCZOS)
    # right column: crest above the number, centred on x = 64% of the face, block centred vertically
    cx=int(BS*.645);lh=int(BS*.27);nh=int(BS*.17);gap=int(BS*.035);top=(BS-(lh+gap+nh))//2
    lg=fit_logo(lh);crest=blank(BS,BS);crest.alpha_composite(lg,(cx-lg.width//2,top))
    nm=number(num,nh);numL=blank(BS,BS);col=Image.new('RGBA',nm.size,(0,0,0,255));col.putalpha(nm);numL.alpha_composite(col,(cx-nm.width//2,top+lh+gap))
    return bg,tr,crest,numL
def btn_guides(pos,num):
    L=[];im=blank(BS,BS);d=ImageDraw.Draw(im);c=BS/2;r=c*.97
    d.ellipse((c-r,c-r,c+r,c+r),outline=(255,0,170,255),width=5);L.append(('Visible face (glass edge)',im))
    im=blank(BS,BS);d=ImageDraw.Draw(im)
    x0,x1,y0,y1=int(BS*.17),int(BS*.47),int(BS*.24),int(BS*.76)
    for x in range(x0,x1,24):d.line((x,y0,x+12,y0),fill=(0,190,255,255),width=4);d.line((x,y1,x+12,y1),fill=(0,190,255,255),width=4)
    for y in range(y0,y1,24):d.line((x0,y,x0,y+12),fill=(0,190,255,255),width=4);d.line((x1,y,x1,y+12),fill=(0,190,255,255),width=4)
    fr=ImageFont.truetype(FONT_R,24);d.text(((x0+x1)//2,(y0+y1)//2),'foto',font=fr,fill=(0,190,255,255),anchor='mm');L.append(('Photo area',im))
    im=blank(BS,BS);d=ImageDraw.Draw(im);fb=ImageFont.truetype(FONT_B,38)
    d.text((34,26),f"Posição {pos}  ·  camisa {num}",font=fb,fill=(255,255,255,255),stroke_width=5,stroke_fill=(17,24,34,255));L.append(('Notes',im))
    return L
def gk_layers(num):
    bg=Image.new('RGBA',(KW,KH),(255,255,255,255))
    tr=blank(KW,KH);d=ImageDraw.Draw(tr);w=int(KH*.075);d.rectangle((0,0,KW-1,KH-1),outline=(0,0,0,255),width=w)
    lh=int(KH*.44);nh=int(KH*.27);gap=int(KH*.04);top=(KH-(lh+gap+nh))//2;cx=int(KW*.80)
    lg=fit_logo(lh);crest=blank(KW,KH);crest.alpha_composite(lg,(cx-lg.width//2,top))
    nm=number(num,nh);numL=blank(KW,KH);col=Image.new('RGBA',nm.size,(0,0,0,255));col.putalpha(nm);numL.alpha_composite(col,(cx-nm.width//2,top+lh+gap))
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
for pos,ox,oy in spots:
    num=MAP[pos];bg,tr,cr,nm=btn_layers(num);g=btn_guides(pos,num);off=(ox,oy)
    board=Image.new('RGBA',(BS,BS),BG+(255,))
    for im in (bg,tr,cr,nm)+tuple(x[1] for x in g):board.alpha_composite(im)
    comp.alpha_composite(board,off)
    guide=group('Guides (hide before export)',[Layer(n,im,off) for n,im in reversed(g)])
    recs+=group(str(pos),[guide,Layer(f'Número {num}',nm,off),Layer('Escudo',cr,off),Layer('Trim (preto)',tr,off),Layer('Foto (coloque aqui)',None),Layer('Fundo (branco)',bg,off)],artboard=((ox,oy,ox+BS,oy+BS),BG))
kx=(W-KW)//2;ky=GAP*2+BS;off=(kx,ky);num=MAP[1]
bg,tr,cr,nm=gk_layers(num);g=gk_guides(num);board=Image.new('RGBA',(KW,KH),BG+(255,))
for im in (bg,tr,cr,nm)+tuple(x[1] for x in g):board.alpha_composite(im)
comp.alpha_composite(board,off)
guide=group('Guides (hide before export)',[Layer(n,im,off) for n,im in reversed(g)])
recs+=group('1',[guide,Layer(f'Número {num}',nm,off),Layer('Escudo',cr,off),Layer('Trim (preto)',tr,off),Layer('Foto (coloque aqui)',None),Layer('Fundo (branco)',bg,off)],artboard=((kx,ky,kx+KW,ky+KH),BG))
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
