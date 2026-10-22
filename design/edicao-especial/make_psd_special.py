"""Botonista special-edition kit: one PSD with an artboard per box piece.
Artboards are named 2..11 and GK, so Photoshop's File > Export > Artboards to Files with a prefix like 'COR_'
writes COR_2.png ... COR_11.png and COR_GK.png.
Buttons: 1024 x 1024 (the game uses 512 square), Keeper: 1960 x 680 (2x the game's 980 x 340 card)."""
import struct, sys
from PIL import Image, ImageDraw, ImageFont
FONT_B='/usr/share/fonts/opentype/inter/Inter-Bold.otf'; FONT_R='/usr/share/fonts/opentype/inter/Inter-Regular.otf'
BS=1024; KWp,KHp=1960,680; GAP=160
def packbits(row):
    out=bytearray(); i=0; n=len(row)
    while i<n:
        j=i
        while j+1<n and row[j+1]==row[i] and j-i<127: j+=1
        if j>i:
            out.append((257-(j-i+1))&255); out.append(row[i]); i=j+1
        else:
            j=i
            while j<n and j-i<128 and not (j+2<n and row[j]==row[j+1]==row[j+2]): j+=1
            if j==i: j=i+1
            out.append(j-i-1); out+=row[i:j]; i=j
    return bytes(out)
def rle_channel(data,w,h):
    rows=[packbits(data[y*w:(y+1)*w]) for y in range(h)]
    # keep each channel an even number of bytes (0x80 is a PackBits no-op); some readers expect it
    if (2+2*h+sum(len(r) for r in rows))%2: rows[-1]=rows[-1]+b'\x80'
    return struct.pack('>'+'H'*h,*[len(r) for r in rows])+b''.join(rows)

def ustr(s): return struct.pack('>I',len(s)+1)+s.encode('utf-16-be')+b'\0\0'
def key(k):
    return struct.pack('>I',0)+k.encode() if len(k)==4 else struct.pack('>I',len(k))+k.encode()
def desc(cls,items):
    b=ustr('')+key(cls)+struct.pack('>I',len(items))
    for k,t,v in items:
        b+=key(k)+t.encode()
        if t=='doub': b+=struct.pack('>d',v)
        elif t=='long': b+=struct.pack('>i',v)
        elif t=='TEXT': b+=ustr(v)
        elif t=='Objc': b+=desc(*v)
        elif t=='VlLs': b+=struct.pack('>I',0)
    return b
def block(k,data):
    if len(data)%4: data+=b'\0'*(4-len(data)%4)
    return b'8BIM'+k.encode()+struct.pack('>I',len(data))+data
def pascal(name):
    n=name.encode('latin-1','replace')[:255]; b=bytes([len(n)])+n
    return b+b'\0'*((4-len(b)%4)%4)

class Layer:
    def __init__(s,name,img=None,off=(0,0),kind='pixel',opacity=255,hidden=False,artboard=None,blend='norm'):
        s.name=name;s.kind=kind;s.opacity=opacity;s.hidden=hidden;s.artboard=artboard;s.blend=blend
        s.rect=(0,0,0,0);s.chans={}
        if img is not None:
            bb=img.getbbox()
            if bb is None: bb=(0,0,1,1)
            im=img.crop(bb); l,t=off[0]+bb[0],off[1]+bb[1]
            s.rect=(t,l,t+im.height,l+im.width)
            r,g,b,a=im.split()
            for cid,ch in ((-1,a),(0,r),(1,g),(2,b)):
                s.chans[cid]=b'\0\1'+rle_channel(ch.tobytes(),im.width,im.height)
        else:
            for cid in (-1,0,1,2): s.chans[cid]=b'\0\0'
    def record(s):
        t,l,b,r=s.rect
        rec=struct.pack('>iiiiH',t,l,b,r,4)
        for cid in (-1,0,1,2): rec+=struct.pack('>hI',cid,len(s.chans[cid]))
        flags=(0x02 if s.hidden else 0)|(0x18 if s.kind!='pixel' else 0x08)
        rec+=b'8BIM'+s.blend.encode()+struct.pack('>BBBB',s.opacity,0,flags,0)
        extra=struct.pack('>I',0)+struct.pack('>I',0)+pascal(s.name)
        extra+=block('luni',ustr(s.name)[:-2] if False else struct.pack('>I',len(s.name))+s.name.encode('utf-16-be'))
        if s.kind=='open': extra+=block('lsct',struct.pack('>I',0 if False else 1)+b'8BIMpass')
        if s.kind=='closed': extra+=block('lsct',struct.pack('>I',2)+b'8BIMpass')
        if s.kind=='end': extra+=block('lsct',struct.pack('>I',3))
        if s.artboard:
            (x0,y0,x1,y1),bg=s.artboard
            d=struct.pack('>I',16)+desc('artboard',[
                ('artboardRect','Objc',('classFloatRect',[('Top ','doub',float(y0)),('Left','doub',float(x0)),('Btom','doub',float(y1)),('Rght','doub',float(x1))])),
                ('guideIndeces','VlLs',None),
                ('artboardPresetName','TEXT',''),
                ('Clr ','Objc',('RGBC',[('Rd  ','doub',float(bg[0])),('Grn ','doub',float(bg[1])),('Bl  ','doub',float(bg[2]))])),
                ('artboardBackgroundType','long',3)])
            extra+=block('artb',d)
        rec+=struct.pack('>I',len(extra))+extra
        return rec
    def data(s): return b''.join(s.chans[c] for c in (-1,0,1,2))

def group(name,children,closed=False,artboard=None,hidden=False):
    """children listed top to bottom; returns records bottom to top"""
    out=[Layer('</Layer group>',kind='end')]
    for ch in reversed(children): out+= ch if isinstance(ch,list) else [ch]
    out.append(Layer(name,kind='closed' if closed else 'open',artboard=artboard,hidden=hidden,blend='pass'))
    return out



SS=2
def circ_guides(num):
    L=[]
    im=Image.new('RGBA',(BS*SS,BS*SS),(0,0,0,0));d=ImageDraw.Draw(im);c=BS*SS/2
    r=c*.97;d.ellipse((c-r,c-r,c+r,c+r),outline=(255,0,170,255),width=5*SS)
    L.append(('Visible face (edge of the glass)',im.resize((BS,BS),Image.LANCZOS)))
    im=Image.new('RGBA',(BS,BS),(0,0,0,0));d=ImageDraw.Draw(im);c=BS/2;r=c*.80
    for a in range(0,360,6):
        import math
        a0=math.radians(a);a1=math.radians(a+3);d.line((c+r*math.cos(a0),c+r*math.sin(a0),c+r*math.cos(a1),c+r*math.sin(a1)),fill=(0,190,255,255),width=4)
    L.append(('Safe area',im))
    im=Image.new('RGBA',(BS,BS),(0,0,0,0));d=ImageDraw.Draw(im);fb=ImageFont.truetype(FONT_B,40);fr=ImageFont.truetype(FONT_R,26)
    d.text((40,30),f"#{num}",font=fb,fill=(255,255,255,255),stroke_width=5,stroke_fill=(17,24,34,255))
    d.text((40,BS-70),"Paint the full face, number included. 1024 px square, round crop.",font=fr,fill=(255,255,255,255),stroke_width=4,stroke_fill=(17,24,34,255))
    L.append(('Notes',im))
    return L
def btn_base(num):
    im=Image.new('RGBA',(BS*SS,BS*SS),(0,0,0,0));d=ImageDraw.Draw(im);c=BS*SS/2
    d.rectangle((0,0,BS*SS,BS*SS),fill=(60,66,78,255));r=c*.78;d.ellipse((c-r,c-r,c+r,c+r),fill=(232,234,238,255))
    bg=im.resize((BS,BS),Image.LANCZOS)
    nm=Image.new('RGBA',(BS,BS),(0,0,0,0));d=ImageDraw.Draw(nm);f=ImageFont.truetype(FONT_B,int(BS*.25))
    d.text((BS/2,BS/2+BS*.19),str(num),font=f,fill=(20,24,34,255),anchor='mm')
    return bg,nm
def gk_guides():
    L=[]
    im=Image.new('RGBA',(KWp,KHp),(0,0,0,0));d=ImageDraw.Draw(im);d.rectangle((3,3,KWp-4,KHp-4),outline=(255,0,170,255),width=6);L.append(('Card edge',im))
    im=Image.new('RGBA',(KWp,KHp),(0,0,0,0));d=ImageDraw.Draw(im);m=60
    for x in range(m,KWp-m,30):d.line((x,m,x+15,m),fill=(0,190,255,255),width=4);d.line((x,KHp-m,x+15,KHp-m),fill=(0,190,255,255),width=4)
    for y in range(m,KHp-m,30):d.line((m,y,m,y+15),fill=(0,190,255,255),width=4);d.line((KWp-m,y,KWp-m,y+15),fill=(0,190,255,255),width=4)
    L.append(('Safe area',im))
    im=Image.new('RGBA',(KWp,KHp),(0,0,0,0));d=ImageDraw.Draw(im);fb=ImageFont.truetype(FONT_B,44);fr=ImageFont.truetype(FONT_R,28)
    d.text((80,70),"GK  Goleiro",font=fb,fill=(255,255,255,255),stroke_width=5,stroke_fill=(17,24,34,255))
    d.text((80,KHp-110),"1960 x 680 px (2x the game's 980 x 340). Seen through the front of the glass block.",font=fr,fill=(255,255,255,255),stroke_width=4,stroke_fill=(17,24,34,255))
    L.append(('Notes',im));return L
W=5*BS+6*GAP; H=GAP*4+BS*2+KHp
BG=(238,241,240)
composite=Image.new('RGBA',(W,H),(214,219,216,255));records=[]
spots=[(str(n),GAP+i*(BS+GAP),GAP) for i,n in enumerate(range(2,7))]+[(str(n),GAP+i*(BS+GAP),GAP*3+BS+KHp) for i,n in enumerate(range(7,12))]
for name,ox,oy in spots:
    bg,nm=btn_base(int(name));g=circ_guides(name);off=(ox,oy)
    board=Image.new('RGBA',(BS,BS),BG+(255,))
    for im in (bg,nm)+tuple(x[1] for x in g):board.alpha_composite(im)
    composite.alpha_composite(board,off)
    base=group('Template (hide or delete)',[Layer('Number (game position)',nm,off),Layer('Placeholder face',bg,off)])
    guide=group('Guides (hide before export)',[Layer(n,im,off) for n,im in reversed(g)])
    records+=group(name,[guide,Layer('Artwork (paint here)',None),base],artboard=((ox,oy,ox+BS,oy+BS),BG))
kx=(W-KWp)//2;ky=GAP*2+BS;off=(kx,ky)
gb=Image.new('RGBA',(KWp,KHp),(60,66,78,255));g=gk_guides()
board=Image.new('RGBA',(KWp,KHp),BG+(255,));board.alpha_composite(gb)
for _,im in g:board.alpha_composite(im)
composite.alpha_composite(board,off)
base=group('Template (hide or delete)',[Layer('Placeholder card',gb,off)])
guide=group('Guides (hide before export)',[Layer(n,im,off) for n,im in reversed(g)])
records+=group('GK',[guide,Layer('Artwork (paint here)',None),base],artboard=((kx,ky,kx+KWp,ky+KHp),BG))
layer_info=struct.pack('>h',-len(records))
layer_info+=b''.join(L.record() for L in records)
layer_info+=b''.join(L.data() for L in records)
if len(layer_info)%2: layer_info+=b'\0'
layer_info=struct.pack('>I',len(layer_info))+layer_info
lmi=layer_info+struct.pack('>I',0)
lmi=struct.pack('>I',len(lmi))+lmi
hdr=b'8BPS'+struct.pack('>H',1)+b'\0'*6+struct.pack('>HIIHH',4,H,W,8,3)
out=hdr+struct.pack('>I',0)+struct.pack('>I',0)+lmi
counts=b'';datas=b''
for ch in composite.split():
    raw=ch.tobytes(); rws=[packbits(raw[y*W:(y+1)*W]) for y in range(H)]
    counts+=struct.pack('>'+'H'*H,*[len(x) for x in rws]); datas+=b''.join(rws)
out+=struct.pack('>H',1)+counts+datas
open(sys.argv[1],'wb').write(out)
composite.convert('RGB').resize((W//5,H//5),Image.LANCZOS).save(sys.argv[2])
print(sys.argv[1],len(out)//1024,'KB',W,H,len(records),'records')
