import random,math,os,sys
W,H=640,360
def svg(body,defs=''): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><defs>{defs}<filter id="b"><feGaussianBlur stdDeviation="6"/></filter><filter id="b2"><feGaussianBlur stdDeviation="2"/></filter></defs>{body}</svg>'
def grad(i,stops,x2=0,y2=1): return f'<linearGradient id="{i}" x1="0" y1="0" x2="{x2}" y2="{y2}">'+''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o,c in stops)+'</linearGradient>'
R=random.Random(5)
A={}
# 1 crimson dojo
d=grad('s',[(0,'#1c0b24'),(.5,'#7a1f3a'),(1,'#ff8a3d')])
b=f'<rect width="{W}" height="{H}" fill="url(#s)"/><circle cx="320" cy="170" r="92" fill="#ffd27a" opacity=".95"/><circle cx="320" cy="170" r="130" fill="#ff8a3d" opacity=".35" filter="url(#b)"/>'
b+='<polygon points="0,230 80,150 150,215 230,130 320,225 420,140 520,220 600,160 640,200 640,260 0,260" fill="#2a0f24"/>'
b+='<g fill="#c4262e" stroke="#3a0a14" stroke-width="3"><rect x="200" y="120" width="16" height="150"/><rect x="424" y="120" width="16" height="150"/><path d="M170,118 Q320,92 470,118 L460,138 Q320,116 180,138Z"/><rect x="198" y="158" width="244" height="12"/></g>'
b+=f'<rect y="260" width="{W}" height="100" fill="#3b1a1a"/>'+''.join(f'<line x1="0" y1="{270+i*14}" x2="{W}" y2="{270+i*14}" stroke="#5a2a22" stroke-width="2"/>' for i in range(7))
for x in (60,130,510,580): b+=f'<line x1="{x}" y1="0" x2="{x}" y2="70" stroke="#222" stroke-width="2"/><ellipse cx="{x}" cy="86" rx="20" ry="26" fill="#ff4b3a"/><ellipse cx="{x}" cy="86" rx="30" ry="36" fill="#ff7a4a" opacity=".4" filter="url(#b)"/>'
for i in range(40): x,y=R.uniform(0,W),R.uniform(0,H); b+=f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="5" ry="3" fill="#ffb6c9" opacity=".85" transform="rotate({R.uniform(0,180):.0f} {x:.0f} {y:.0f})"/>'
A['crimson-dojo']=svg(b,d)
# 2 frozen citadel
d=grad('s',[(0,'#050a1f'),(.6,'#0b3a5a'),(1,'#1b7a9a')])+grad('au',[(0,'#3dffb0'),(1,'#a56bff')],1,0)
b=f'<rect width="{W}" height="{H}" fill="url(#s)"/>'
for i,(y,o) in enumerate([(70,.5),(110,.35),(150,.25)]): b+=f'<path d="M0,{y} Q160,{y-60} 320,{y} T640,{y-10} L640,{y+60} Q480,{y+10} 320,{y+70} T0,{y+50}Z" fill="url(#au)" opacity="{o}" filter="url(#b)"/>'
b+='<g fill="#0a2238"><rect x="250" y="120" width="40" height="150"/><rect x="300" y="90" width="50" height="180"/><rect x="360" y="130" width="36" height="140"/><polygon points="300,90 325,40 350,90"/></g>'
b+=f'<rect y="262" width="{W}" height="98" fill="#7fc8ee"/><rect y="262" width="{W}" height="98" fill="url(#s)" opacity=".35"/>'
for x,h,w in [(40,150,40),(110,110,30),(520,160,44),(590,100,30),(170,70,24),(460,80,26)]: b+=f'<polygon points="{x},262 {x+w/2},{262-h} {x+w},262" fill="#9fe6ff" stroke="#e8fbff" stroke-width="2"/><polygon points="{x+w/2},{262-h} {x+w},262 {x+w*.55},262" fill="#5fc4ee" opacity=".7"/>'
for i in range(70): b+=f'<circle cx="{R.uniform(0,W):.0f}" cy="{R.uniform(0,H):.0f}" r="{R.uniform(1,2.8):.1f}" fill="#fff" opacity=".8"/>'
A['frozen-citadel']=svg(b,d)
# 3 volcano forge
d=grad('s',[(0,'#090305'),(.55,'#4a0f12'),(1,'#d4401a')])+grad('lv',[(0,'#ffd27a'),(1,'#ff3d00')])
b=f'<rect width="{W}" height="{H}" fill="url(#s)"/><polygon points="170,270 320,80 470,270" fill="#1a0a0c"/><polygon points="290,100 320,80 350,100 335,118 305,118" fill="url(#lv)"/><ellipse cx="320" cy="90" rx="90" ry="40" fill="#ff5a1a" opacity=".5" filter="url(#b)"/>'
b+='<path d="M312,118 Q300,180 320,230 Q335,180 328,118Z" fill="url(#lv)" opacity=".9"/>'
for x,h in [(40,170),(110,120),(530,180),(600,130)]: b+=f'<polygon points="{x-26},270 {x},{270-h} {x+26},270" fill="#14070a" stroke="#ff5a1a" stroke-width="1.5"/>'
b+=f'<rect y="262" width="{W}" height="98" fill="#150a0c"/>'
for i in range(12): x=R.uniform(20,620); y=R.uniform(270,350); b+=f'<polyline points="{x:.0f},{y:.0f} {x+R.uniform(-40,40):.0f},{y+R.uniform(8,20):.0f} {x+R.uniform(-60,60):.0f},{y+R.uniform(18,34):.0f}" fill="none" stroke="#ff7a2a" stroke-width="3" filter="url(#b2)"/>'
b+='<path d="M0,330 Q160,300 320,335 T640,320 L640,360 L0,360Z" fill="url(#lv)" opacity=".85"/>'
for i in range(60): b+=f'<circle cx="{R.uniform(0,W):.0f}" cy="{R.uniform(0,H):.0f}" r="{R.uniform(1,3):.1f}" fill="#ffb347" opacity="{R.uniform(.4,1):.2f}"/>'
A['volcano-forge']=svg(b,d)
# 4 storm peak
d=grad('s',[(0,'#05070f'),(.7,'#1a2438'),(1,'#33425c')])
b=f'<rect width="{W}" height="{H}" fill="url(#s)"/>'
for i in range(9): x=R.uniform(0,W); y=R.uniform(10,130); b+=f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{R.uniform(90,170):.0f}" ry="{R.uniform(24,44):.0f}" fill="#0b1019" opacity=".85"/>'
b+='<polyline points="360,0 340,60 372,92 332,150 364,180 322,260" fill="none" stroke="#bfe6ff" stroke-width="6" filter="url(#b2)"/><polyline points="360,0 340,60 372,92 332,150 364,180 322,260" fill="none" stroke="#fff" stroke-width="2.5"/><ellipse cx="350" cy="120" rx="140" ry="110" fill="#8ec8ff" opacity=".18" filter="url(#b)"/>'
b+=f'<rect y="262" width="{W}" height="98" fill="#2a3446"/>'+'<ellipse cx="320" cy="300" rx="190" ry="26" fill="none" stroke="#6fd8ff" stroke-width="4" filter="url(#b2)"/><ellipse cx="320" cy="300" rx="190" ry="26" fill="none" stroke="#e6f6ff" stroke-width="1.5"/>'
for x in (70,150,490,570): b+=f'<rect x="{x-18}" y="110" width="36" height="160" fill="#8b97ad" stroke="#1b2030" stroke-width="3"/><rect x="{x-26}" y="100" width="52" height="14" fill="#9aa6bc" stroke="#1b2030" stroke-width="3"/>'
b+='<rect x="52" y="70" width="190" height="14" fill="#7a869c" stroke="#1b2030" stroke-width="3"/><rect x="400" y="70" width="190" height="14" fill="#7a869c" stroke="#1b2030" stroke-width="3"/>'
for i in range(90): x=R.uniform(0,W);y=R.uniform(0,H); b+=f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x-6:.0f}" y2="{y+22:.0f}" stroke="#9fc2ff" stroke-width="1.4" opacity=".55"/>'
A['storm-peak']=svg(b,d)
# 5 digital void
d=grad('s',[(0,'#02030a'),(.6,'#0a0f2a'),(1,'#1a0a3a')])
b=f'<rect width="{W}" height="{H}" fill="url(#s)"/>'
for i in range(46): x=R.uniform(0,W);y=R.uniform(0,230); h=R.uniform(30,110); b+=f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x:.0f}" y2="{y+h:.0f}" stroke="#3dffb0" stroke-width="2.2" opacity="{R.uniform(.25,.8):.2f}"/><rect x="{x-2:.0f}" y="{y+h:.0f}" width="5" height="5" fill="#d8fff0"/>'
b+='<ellipse cx="320" cy="150" rx="120" ry="120" fill="none" stroke="#ff4fd8" stroke-width="10" filter="url(#b2)"/><ellipse cx="320" cy="150" rx="120" ry="120" fill="none" stroke="#fff" stroke-width="2.5"/><ellipse cx="320" cy="150" rx="86" ry="86" fill="none" stroke="#68f7ff" stroke-width="5" opacity=".9"/><circle cx="320" cy="150" r="60" fill="#68f7ff" opacity=".18" filter="url(#b)"/>'
b+=f'<rect y="262" width="{W}" height="98" fill="#070a1c"/>'
for i in range(14): x=-200+i*90; b+=f'<line x1="{320+(x-320)*.2:.0f}" y1="262" x2="{x:.0f}" y2="360" stroke="#68f7ff" stroke-width="1.6" opacity=".7"/>'
for i in range(6): y=262+(i**1.7)*8; b+=f'<line x1="0" y1="{y:.0f}" x2="{W}" y2="{y:.0f}" stroke="#68f7ff" stroke-width="1.6" opacity=".7"/>'
for i in range(10): x,y=R.uniform(30,610),R.uniform(40,240); s=R.uniform(12,30); b+=f'<rect x="{x:.0f}" y="{y:.0f}" width="{s:.0f}" height="{s:.0f}" fill="none" stroke="#ff4fd8" stroke-width="2.4" transform="rotate({R.uniform(0,60):.0f} {x:.0f} {y:.0f})"/>'
A['digital-void']=svg(b,d)
# 6 neon rift
d=grad('s',[(0,'#04060c'),(.7,'#0a1424'),(1,'#16304a')])
b=f'<rect width="{W}" height="{H}" fill="url(#s)"/><circle cx="470" cy="70" r="46" fill="#bfd8ff" opacity=".9"/>'
for i in range(20): x=i*34; h=R.uniform(60,190); b+=f'<rect x="{x}" y="{262-h:.0f}" width="26" height="{h:.0f}" fill="#0c1424" stroke="#1b2d48" stroke-width="2"/>'+''.join(f'<rect x="{x+5+(j%2)*10}" y="{262-h+8+j*12:.0f}" width="5" height="6" fill="{"#39cde1" if i%2 else "#f14b77"}"/>' for j in range(int(h/14)))
b+=f'<rect y="262" width="{W}" height="98" fill="#0e1828"/>'+''.join(f'<ellipse cx="320" cy="310" rx="{110+i*55}" ry="{18+i*8}" fill="none" stroke="{"#ff496d" if i==1 else "#44dbe8"}" stroke-width="3" opacity=".8"/>' for i in range(3))
for x,c in ((70,'#3be4e4'),(570,'#ff4b6b')): b+=f'<rect x="{x-12}" y="120" width="24" height="150" fill="#11192a" stroke="{c}" stroke-width="3"/><rect x="{x-3}" y="150" width="6" height="60" fill="{c}"/>'
A['neon-rift']=svg(b,d)
os.makedirs('arena_svg',exist_ok=True)
for k,v in A.items(): open(f'arena_svg/{k}.svg','w').write(v)
print(list(A))
