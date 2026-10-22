// standalone preview renderer for the box GLB, run inside the game page (needs ALLT, GK_ART, team objects)
async (args)=>{
const {b64,codes,W,H,yaw,el,away}=args;
const bin=Uint8Array.from(atob(b64),c=>c.charCodeAt(0)).buffer,dv=new DataView(bin);
const jl=dv.getUint32(12,true),J=JSON.parse(new TextDecoder().decode(new Uint8Array(bin,20,jl)));
const bo=20+jl,bl=dv.getUint32(bo,true),BIN=new Uint8Array(bin,bo+8,bl);
const acc=i=>{const a=J.accessors[i],v=J.bufferViews[a.bufferView],n={SCALAR:1,VEC2:2,VEC3:3,VEC4:4}[a.type],off=(v.byteOffset||0)+(a.byteOffset||0);
  const T={5126:Float32Array,5123:Uint16Array,5125:Uint32Array,5121:Uint8Array}[a.componentType];return new T(BIN.buffer.slice(BIN.byteOffset+off,BIN.byteOffset+off+a.count*n*T.BYTES_PER_ELEMENT))};
const cv=document.createElement('canvas');cv.width=W;cv.height=H;const gl=cv.getContext('webgl2',{antialias:true,premultipliedAlpha:true,preserveDrawingBuffer:true});
const VS=`#version 300 es
in vec3 aP;in vec3 aN;in vec2 aT;uniform mat4 uM,uVP;out vec3 vW;out vec3 vN;out vec2 vT;
void main(){vec4 w=uM*vec4(aP,1.);vW=w.xyz;vN=mat3(uM)*aN;vT=aT;gl_Position=uVP*w;}`;
const FS=`#version 300 es
precision highp float;in vec3 vW;in vec3 vN;in vec2 vT;out vec4 o;
uniform vec3 uCam,uCol;uniform float uRough,uMode,uA;uniform sampler2D uTex;
vec3 env(vec3 R){vec3 c=mix(vec3(.10,.10,.11),vec3(.55,.58,.64),smoothstep(-.2,.6,R.y));
  float s=max(dot(normalize(R),normalize(vec3(-.4,.85,.35))),0.);c+=vec3(1.)*(pow(s,60.)*2.5+pow(s,8.)*.25);
  float s2=max(dot(normalize(R),normalize(vec3(.7,.5,-.5))),0.);c+=vec3(.9,.95,1.)*pow(s2,40.)*.8;return c;}
void main(){vec3 N=normalize(vN),V=normalize(uCam-vW);if(dot(N,V)<0.)N=-N;
  vec3 L=normalize(vec3(-.4,.85,.35)),H=normalize(L+V),R=reflect(-V,N);float F=.04+.96*pow(1.-max(dot(N,V),0.),5.);
  float sh=mix(900.,12.,uRough),sp=pow(max(dot(N,H),0.),sh)*mix(1.2,.12,uRough);
  float diff=max(dot(N,L),0.),amb=.38+.22*N.y;
  if(uMode>1.5&&uMode<2.5){float Fg=min(1.,F*1.5+.04);vec3 c=env(R)*Fg+vec3(sp)*1.3;float a=clamp(Fg+sp+.05,0.,1.)*uA;o=vec4(c*uA,a);return;}
  vec4 tx=texture(uTex,vT);vec3 base=uMode>.5?tx.rgb:uCol;
  vec3 c=base*(diff*.6+amb*.7)+vec3(sp)+env(R)*F*(1.-uRough)*.6;float al=uMode>2.5?tx.a:1.;o=vec4(c*al,al);}`;
const sh=(t,s)=>{const x=gl.createShader(t);gl.shaderSource(x,s);gl.compileShader(x);if(!gl.getShaderParameter(x,gl.COMPILE_STATUS))throw gl.getShaderInfoLog(x);return x};
const pr=gl.createProgram();gl.attachShader(pr,sh(gl.VERTEX_SHADER,VS));gl.attachShader(pr,sh(gl.FRAGMENT_SHADER,FS));gl.bindAttribLocation(pr,0,'aP');gl.bindAttribLocation(pr,1,'aN');gl.bindAttribLocation(pr,2,'aT');gl.linkProgram(pr);gl.useProgram(pr);
const U=n=>gl.getUniformLocation(pr,n);
// matrices
const mul=(a,b)=>{const o=new Float32Array(16);for(let i=0;i<4;i++)for(let j=0;j<4;j++){let s=0;for(let k=0;k<4;k++)s+=a[k*4+j]*b[i*4+k];o[i*4+j]=s}return o};
const TRS=n=>{const t=n.translation||[0,0,0],q=n.rotation||[0,0,0,1],s=n.scale||[1,1,1],[x,y,z,w]=q;
  return new Float32Array([(1-2*(y*y+z*z))*s[0],(2*(x*y+z*w))*s[0],(2*(x*z-y*w))*s[0],0,(2*(x*y-z*w))*s[1],(1-2*(x*x+z*z))*s[1],(2*(y*z+x*w))*s[1],0,(2*(x*z+y*w))*s[2],(2*(y*z-x*w))*s[2],(1-2*(x*x+y*y))*s[2],0,t[0],t[1],t[2],1])};
// geometry
const items=[];
J.nodes.forEach(n=>{if(n.mesh==null)return;const M0=TRS(n);J.meshes[n.mesh].primitives.forEach(p=>{
  // the keeper lies on its back, so its art card ends up facing the floor: mirror it to just under the top glass, facing up
  const M=(/Keeper/.test(n.name)&&J.materials[p.material].name==='Arte')?mul(M0,new Float32Array([1,0,0,0,0,1,0,0,0,0,-1,0,0,0,0,1])):M0;
  const va=gl.createVertexArray();gl.bindVertexArray(va);
  [['POSITION',0,3],['NORMAL',1,3],['TEXCOORD_0',2,2]].forEach(([k,l,c])=>{const b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,acc(p.attributes[k]),gl.STATIC_DRAW);gl.enableVertexAttribArray(l);gl.vertexAttribPointer(l,c,gl.FLOAT,false,0,0)});
  const ix=acc(p.indices),ib=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,ix,gl.STATIC_DRAW);
  const a=J.accessors[p.attributes.POSITION],c=[0,1,2].map(i=>(a.min[i]+a.max[i])/2);
  const wc=[0,1,2].map(i=>M[i]*c[0]+M[4+i]*c[1]+M[8+i]*c[2]+M[12+i]);
  items.push({node:n.name,mat:J.materials[p.material].name,va,n:ix.length,type:ix instanceof Uint32Array?gl.UNSIGNED_INT:gl.UNSIGNED_SHORT,M,wc})})});
// which art disc is which shirt number: top row (z<0) 2..6 left to right, bottom row 7..11
const discs=items.filter(i=>i.mat==='Arte'&&!/Keeper/.test(i.node)).sort((a,b)=>(a.wc[2]>0)-(b.wc[2]>0)||a.wc[0]-b.wc[0]);discs.forEach((d,i)=>d.num=i+2);
const rgb=h=>{const n=parseInt(h.slice(1),16);return [(n>>16)/255,(n>>8&255)/255,(n&255)/255]};
const tex=c=>{const t=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,t);gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,false);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,c);gl.generateMipmap(gl.TEXTURE_2D);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR_MIPMAP_LINEAR);return t};
const btnCanvas=(team,num)=>{const N=512,c=document.createElement('canvas');c.width=c.height=N;const x=c.getContext('2d');
  if(team.img&&team.img.complete&&team.img.naturalWidth)x.drawImage(team.img,0,0,N,N);else{x.fillStyle=team.ring;x.fillRect(0,0,N,N)}
  x.fillStyle=team.num;x.font=`700 ${N*.25}px Geist, system-ui, sans-serif`;x.textAlign='center';x.textBaseline='middle';x.fillText(num,N/2,N/2+N*.19);return c};
const gkCanvas=team=>{const im=gkImg(team);const c=document.createElement('canvas');c.width=980;c.height=340;const x=c.getContext('2d');x.fillStyle=team.ring;x.fillRect(0,0,980,340);if(im&&im.complete&&im.naturalWidth)x.drawImage(im,0,0,980,340);return c};
// camera
const tgt=[0,0,0],dist=.78,cp=[tgt[0]+Math.sin(yaw)*Math.cos(el)*dist,tgt[1]+Math.sin(el)*dist,tgt[2]+Math.cos(yaw)*Math.cos(el)*dist];
const f=[tgt[0]-cp[0],tgt[1]-cp[1],tgt[2]-cp[2]].map((v,_,a)=>v/Math.hypot(...a));const up=[0,1,0];
let r=[f[1]*up[2]-f[2]*up[1],f[2]*up[0]-f[0]*up[2],f[0]*up[1]-f[1]*up[0]];const rl=Math.hypot(...r);r=r.map(v=>v/rl);const u=[r[1]*f[2]-r[2]*f[1],r[2]*f[0]-r[0]*f[2],r[0]*f[1]-r[1]*f[0]];
const dd=v=>v[0]*cp[0]+v[1]*cp[1]+v[2]*cp[2],fov=.62,asp=W/H,ny=.05,fy=10,A=-(fy+ny)/(fy-ny),B=-2*fy*ny/(fy-ny),sy=1/Math.tan(fov/2),sx=sy/asp;
const view=new Float32Array([r[0],u[0],-f[0],0,r[1],u[1],-f[1],0,r[2],u[2],-f[2],0,-dd(r),-dd(u),dd(f),1]);
const proj=new Float32Array([sx,0,0,0,0,sy,0,0,0,0,A,-1,0,0,B,0]);const VP=mul(proj,view);
gl.uniformMatrix4fv(U('uVP'),false,VP);gl.uniform3f(U('uCam'),...cp);
const outs={};
// ---- the cardboard sleeve: a printed frame over the top with a window, its edges folded down a little ----
const FX0=-.1966,FX1=.1966,FZ0=-.1273,FZ1=.1273,WX=.18,WZ0=-.102,WZ1=.106,FY=.0418,FT=.0016,FD=.0436+.0292; // the sleeve hugs the box: same outline, sides all the way down
const mkMesh=(P,N,T,I)=>{const va=gl.createVertexArray();gl.bindVertexArray(va);[[P,0,3],[N,1,3],[T,2,2]].forEach(([a,l,c])=>{const b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(a),gl.STATIC_DRAW);gl.enableVertexAttribArray(l);gl.vertexAttribPointer(l,c,gl.FLOAT,false,0,0)});
  const ib=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint32Array(I),gl.STATIC_DRAW);return {va,n:I.length,type:gl.UNSIGNED_INT,M:new Float32Array([1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1])}};
const quad=(G,ps,n,uvf)=>{const k=G.P.length/3;for(const p of ps){G.P.push(...p);G.N.push(...n);G.T.push(...(uvf?uvf(p):[0,0]))}G.I.push(k,k+1,k+2,k,k+2,k+3)};
const uvTop=p=>[(p[0]-FX0)/(FX1-FX0),(p[2]-FZ0)/(FZ1-FZ0)];
const top={P:[],N:[],T:[],I:[]},side={P:[],N:[],T:[],I:[]},y=FY+FT;
// top surface: four bands around the window
for(const [a,b,c,d] of [[FX0,FZ0,FX1,WZ0],[FX0,WZ1,FX1,FZ1],[FX0,WZ0,-WX,WZ1],[WX,WZ0,FX1,WZ1]])quad(top,[[a,y,b],[c,y,b],[c,y,d],[a,y,d]],[0,1,0],uvTop);
// outer skirt folded down over the box, and the cut edge of the window
quad(side,[[FX0,y,FZ1],[FX1,y,FZ1],[FX1,y-FD,FZ1],[FX0,y-FD,FZ1]],[0,0,1]);quad(side,[[FX0,y,FZ0],[FX1,y,FZ0],[FX1,y-FD,FZ0],[FX0,y-FD,FZ0]],[0,0,-1]);
quad(side,[[FX0,y,FZ0],[FX0,y,FZ1],[FX0,y-FD,FZ1],[FX0,y-FD,FZ0]],[-1,0,0]);quad(side,[[FX1,y,FZ0],[FX1,y,FZ1],[FX1,y-FD,FZ1],[FX1,y-FD,FZ0]],[1,0,0]);
quad(side,[[-WX,y,WZ0],[WX,y,WZ0],[WX,FY,WZ0],[-WX,FY,WZ0]],[0,0,1]);quad(side,[[-WX,y,WZ1],[WX,y,WZ1],[WX,FY,WZ1],[-WX,FY,WZ1]],[0,0,-1]);
quad(side,[[-WX,y,WZ0],[-WX,y,WZ1],[-WX,FY,WZ1],[-WX,FY,WZ0]],[1,0,0]);quad(side,[[WX,y,WZ0],[WX,y,WZ1],[WX,FY,WZ1],[WX,FY,WZ0]],[-1,0,0]);
const frTop=mkMesh(top.P,top.N,top.T,top.I),frSide=mkMesh(side.P,side.N,side.T,side.I);
// the logo sticker on the top-left corner, overlapping the window a little like the brand badge on a real box
const LG={P:[],N:[],T:[],I:[]},ls=.062,lx=FX0+.006,lz=FZ0+.006;quad(LG,[[lx,y+.0004,lz],[lx+ls,y+.0004,lz],[lx+ls,y+.0004,lz+ls],[lx,y+.0004,lz+ls]],[0,1,0],p=>[(p[0]-lx)/ls,(p[2]-lz)/ls]);
const logoM=mkMesh(LG.P,LG.N,LG.T,LG.I);
const lumH=h=>{const [r,g,b]=rgb(h);return .3*r+.59*g+.11*b};
const logoCanvas=(()=>{const N=512,c=document.createElement('canvas');c.width=c.height=N;const x=c.getContext('2d'),C=N/2;
  // soft drop shadow, yellow ring, then the dark puck with its grooves (the app icon)
  x.fillStyle='rgba(0,0,0,.35)';x.filter='blur(10px)';x.beginPath();x.arc(C+6,C+10,N*.44,0,2*Math.PI);x.fill();x.filter='none';
  const yr=x.createLinearGradient(0,0,N,N);yr.addColorStop(0,'#ffe27a');yr.addColorStop(.5,'#ffd23f');yr.addColorStop(1,'#e0ac12');x.fillStyle=yr;x.beginPath();x.arc(C,C,N*.44,0,2*Math.PI);x.fill();
  const pr=N*.33,g=x.createRadialGradient(C-pr*.35,C-pr*.4,pr*.08,C,C,pr);g.addColorStop(0,'#4b5059');g.addColorStop(.55,'#1b1d22');g.addColorStop(1,'#0a0b0d');x.fillStyle=g;x.beginPath();x.arc(C,C,pr,0,2*Math.PI);x.fill();
  x.lineWidth=N*.006;for(const k of [.2,.36,.52,.68,.84]){x.strokeStyle=`rgba(255,255,255,${.10+.06*k})`;x.beginPath();x.arc(C,C,pr*k,0,2*Math.PI);x.stroke()}
  x.strokeStyle='rgba(255,255,255,.35)';x.lineWidth=N*.008;x.beginPath();x.arc(C,C,pr,-2.6,-1.2);x.stroke();
  return c})();
const logoT=tex(logoCanvas);
const frameCanvas=(team,base)=>{const W=2048,H=Math.round(W*(FZ1-FZ0)/(FX1-FX0)),c=document.createElement('canvas');c.width=W;c.height=H;const x=c.getContext('2d');
  const col=lumH(base.dome)>.8?base.ring:base.dome,ink=lumH(col)>.62?'#14182a':'#ffffff',acc=lumH(base.dome)>.8?base.dome:base.ring;
  x.fillStyle=col;x.fillRect(0,0,W,H);
  // cardboard: fine fibres and a soft print sheen
  const id=x.getImageData(0,0,W,H),d=id.data;for(let i=0;i<d.length;i+=4){const n=(Math.random()-.5)*14;d[i]+=n;d[i+1]+=n;d[i+2]+=n}x.putImageData(id,0,0);
  const sh=x.createLinearGradient(0,0,W,H);sh.addColorStop(0,'rgba(255,255,255,.10)');sh.addColorStop(.5,'rgba(255,255,255,0)');sh.addColorStop(1,'rgba(0,0,0,.12)');x.fillStyle=sh;x.fillRect(0,0,W,H);
  const X=v=>(v-FX0)/(FX1-FX0)*W,Z=v=>(v-FZ0)/(FZ1-FZ0)*H;
  // a printed keyline around the window in the team's other colour
  x.strokeStyle=acc;x.lineWidth=W*.003;x.strokeRect(X(-WX)-W*.004,Z(WZ0)-W*.004,X(WX)-X(-WX)+W*.008,Z(WZ1)-Z(WZ0)+W*.008);
  
  const txt=(t,cy,size,sp)=>{let z=size;const set=()=>{x.font=`500 ${z}px Geist, Inter, system-ui, sans-serif`;x.letterSpacing=`${z*sp}px`};set();
    while(x.measureText(t).width>W*.62&&z>20){z-=2;set()}x.textAlign='center';x.textBaseline='middle';x.fillStyle=ink;x.globalAlpha=.96;x.fillText(t,W/2+z*sp/2,cy);x.globalAlpha=1;x.letterSpacing='0px'};
  txt(tn(base).toUpperCase(),Z(WZ0)/2,H*.06,.22);txt('BOTONISTA',(Z(WZ1)+H)/2,H*.045,.42);
  return c};
for(const code of codes){
  const base=ALLT.find(t=>t.c===code);const team=away&&base.away?base.away:base;
  const btex={};discs.forEach(d=>btex[d.num]=tex(btnCanvas(team,d.num)));const gtex=tex(gkCanvas(base));const ftex=tex(frameCanvas(team,base));const fcol=lumH(base.dome)>.8?base.ring:base.dome;
  gl.viewport(0,0,W,H);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.enable(gl.DEPTH_TEST);gl.enable(gl.BLEND);gl.blendFunc(gl.ONE,gl.ONE_MINUS_SRC_ALPHA);gl.disable(gl.CULL_FACE);
  const draw=it=>{gl.uniformMatrix4fv(U('uM'),false,it.M);gl.bindVertexArray(it.va);gl.drawElements(gl.TRIANGLES,it.n,it.type,0)};
  const MATS={BlackPlastic:['#141517',.62],WhitePlastic:['#eceef1',.32],TeamColorTrim:[base.dome,.35]};
  for(const it of items){if(it.mat==='Vidro'||it.mat==='GlassLikeCover'||it.mat==='TeamColorTrim')continue;
    if(it.mat==='Arte'){gl.uniform1f(U('uMode'),1);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,/Keeper/.test(it.node)?gtex:btex[it.num]);gl.uniform1i(U('uTex'),0);gl.uniform1f(U('uRough'),.45)}
    else{const m=MATS[it.mat]||['#888888',.5];gl.uniform1f(U('uMode'),0);gl.uniform3f(U('uCol'),...rgb(m[0]));gl.uniform1f(U('uRough'),m[1])}
    draw(it)}
  gl.uniform1f(U('uMode'),1);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,ftex);gl.uniform1i(U('uTex'),0);gl.uniform1f(U('uRough'),.85);draw(frTop);
  gl.uniform1f(U('uMode'),0);gl.uniform3f(U('uCol'),...rgb(fcol).map(v=>v*.8));draw(frSide);
  const tr=items.filter(it=>it.mat==='Vidro'||it.mat==='GlassLikeCover').sort((a,b)=>Math.hypot(b.wc[0]-cp[0],b.wc[1]-cp[1],b.wc[2]-cp[2])-Math.hypot(a.wc[0]-cp[0],a.wc[1]-cp[1],a.wc[2]-cp[2]));
  gl.depthMask(false);gl.uniform1f(U('uMode'),2);
  for(const it of tr){gl.uniform1f(U('uRough'),.03);gl.uniform1f(U('uA'),it.mat==='GlassLikeCover'?.55:1);draw(it)}
  gl.depthMask(true);
  outs[code]=cv.toDataURL('image/png')}
return JSON.stringify({outs,nodes:items.map(i=>i.node+':'+i.mat+(i.num?'#'+i.num:''))})}
