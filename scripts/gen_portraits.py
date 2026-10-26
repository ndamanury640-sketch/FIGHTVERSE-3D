#!/usr/bin/env python3
"""Procedural anime bust portraits (800x1000 SVG) matching the in-game roster palette/gear."""
import math, random, sys, os

W, H = 800, 1000
CX = 400

def hx(c): return '#%06x' % c
def mix(a, b, t):
    ar, ag, ab = (a >> 16) & 255, (a >> 8) & 255, a & 255
    br, bg, bb = (b >> 16) & 255, (b >> 8) & 255, b & 255
    return (int(ar + (br - ar) * t) << 16) | (int(ag + (bg - ag) * t) << 8) | int(ab + (bb - ab) * t)
dark = lambda c, t=.4: mix(c, 0x05060c, t)
light = lambda c, t=.4: mix(c, 0xffffff, t)

# ---- roster (mirrors game/roster.js) ---------------------------------------------------------------------------
R = {
 'inferno': dict(name='RYUGA', skin=0xf0bf9b, hair=0xff4b1f, hi=0xffb347, eye=0xffa11a, outfit=0x1d1a24, o2=0x2b2330, acc=0xff6a2a, glow=0xff6a1f, glow2=0xffd27a, style='spiky', sweep=.25, spikes=1.0, gear=['vest','headband','flame'], brow=.2, fx='flame'),
 'frostbite': dict(name='YUKINE', skin=0xfde4d6, hair=0xcfeaff, hi=0xffffff, eye=0x4fd6ff, outfit=0x28477a, o2=0x1a2a4a, acc=0xe4f7ff, glow=0x59d8ff, glow2=0xeaffff, style='long', gear=['coat','scarfshort'], fem=True, brow=.0, fx='ice'),
 'volt': dict(name='RAIKO', skin=0xeabb98, hair=0xffe433, hi=0xfffbb0, eye=0xfff26a, outfit=0x1f2438, o2=0x171b2e, acc=0xffd21f, glow=0xfff23a, glow2=0xffffff, style='spiky', sweep=.7, spikes=1.25, gear=['jacket','goggles'], brow=.15, fx='spark'),
 'shadow-reaper': dict(name='KAGEMARU', skin=0xdcae90, hair=0x2b2050, hi=0x8a66ff, eye=0xb86bff, outfit=0x241b3f, o2=0x17112b, acc=0x8a63ff, glow=0xa56bff, glow2=0xe3c8ff, style='messy', gear=['mask','scarf'], brow=.25, fx='void'),
 'titan': dict(name='DAIGO', skin=0xd09d7a, hair=0x3a2a22, hi=0x8a6a50, eye=0xffc65a, outfit=0x6b7488, o2=0x434a5c, acc=0xe0a95b, glow=0xffb44a, glow2=0xfff0b0, style='crop', gear=['armor','headband'], wide=1.14, brow=.32, fx='quake'),
 'cyber-x': dict(name='KAITO-X', skin=0xf3d3bb, hair=0xe9f3ff, hi=0xffffff, eye=0x37c8ff, outfit=0x141b2d, o2=0x0f1526, acc=0x83dfff, glow=0x2aa8ff, glow2=0xbff0ff, style='spiky', sweep=.1, spikes=1.05, gear=['jacket','visor','xemblem'], brow=.2, fx='cyber'),
 'jade-monk': dict(name='SEIRYU', skin=0xe3b189, hair=0x1f6b52, hi=0x6fe0a8, eye=0x6dffb2, outfit=0x2c9a72, o2=0xe9e3c9, acc=0xb7f7a1, glow=0x43ffad, glow2=0xdfffd0, style='topknot', gear=['gi','beads'], brow=.1, fx='jade'),
 'toxic-fang': dict(name='KIBA', skin=0xcfa680, hair=0x18331c, hi=0xa6ff3a, eye=0xc8ff2a, outfit=0x1e2c20, o2=0x131c15, acc=0xb7ff3a, glow=0x9dff35, glow2=0xf0ffb0, style='spiky', sweep=-.45, spikes=1.15, gear=['jacket','claws'], brow=.32, fx='venom'),
 'glitch': dict(name='MIRAI', skin=0xffe3d3, hair=0xff4fd8, hi=0x68f7ff, eye=0x68f7ff, outfit=0x2b1a49, o2=0x1b1232, acc=0x68f7ff, glow=0xff4fd8, glow2=0x9ffcff, style='twin', gear=['jacket','headset'], fem=True, brow=.0, fx='glitch'),
 'storm-ronin': dict(name='ARASHI', skin=0xdfb28f, hair=0x2c3c66, hi=0x9fc2ff, eye=0x8ec8ff, outfit=0x3a62b0, o2=0x1c2744, acc=0xe1e9ff, glow=0x6da9ff, glow2=0xe6f1ff, style='ponytail', gear=['haori','katana'], brow=.2, fx='storm'),
}

def blade(bx, by, tx, ty, w, curve=.18, fill='#000', extra=''):
    """tapered hair lock from base (bx,by) to tip (tx,ty)"""
    dx, dy = tx - bx, ty - by; l = math.hypot(dx, dy) or 1; nx, ny = -dy / l, dx / l
    c1 = (bx + dx * .5 + nx * l * curve, by + dy * .5 + ny * l * curve)
    c2 = (bx + dx * .5 + nx * (l * curve - w * .35), by + dy * .5 + ny * (l * curve - w * .35))
    a = (bx + nx * w / 2, by + ny * w / 2); b = (bx - nx * w / 2, by - ny * w / 2)
    return f'<path d="M{a[0]:.1f},{a[1]:.1f} Q{c1[0]:.1f},{c1[1]:.1f} {tx:.1f},{ty:.1f} Q{c2[0]-nx*w*.55:.1f},{c2[1]-ny*w*.55:.1f} {b[0]:.1f},{b[1]:.1f} Z" fill="{fill}" {extra}/>'

class P:
    def __init__(self, slug):
        self.s = slug; self.d = R[slug]; self.o = []; self.defs = []; self.rnd = random.Random(slug)
        d = self.d
        self.hairD = dark(d['hair'], .45); self.hairL = light(d['hair'], .25); self.skinD = mix(d['skin'], 0x8a4a3a, .28); self.skinDD = mix(d['skin'], 0x5a2a28, .45)
    def add(self, s): self.o.append(s)
    def gid(self, n): return f'{n}_{self.s.replace("-","")}'

    # ---------------------------------------------------------------- background ----
    def background(self):
        d = self.d; g = hx(d['glow']); g2 = hx(d['glow2']); bg1 = hx(dark(d['glow'], .86)); bg2 = hx(dark(d['glow'], .93))
        self.defs.append(f'''<radialGradient id="{self.gid('bg')}" cx="50%" cy="38%" r="75%"><stop offset="0" stop-color="{hx(mix(d['glow'],0x0a0d18,.62))}"/><stop offset=".55" stop-color="{bg1}"/><stop offset="1" stop-color="#04060c"/></radialGradient>
<filter id="{self.gid('blur')}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="14"/></filter>
<filter id="{self.gid('blur2')}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="5"/></filter>
<pattern id="{self.gid('dots')}" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(30)"><circle cx="7" cy="7" r="2.1" fill="{g}" opacity=".5"/></pattern>
<linearGradient id="{self.gid('fade')}" x1="0" y1="0" x2="0" y2="1"><stop offset=".55" stop-color="#04060c" stop-opacity="0"/><stop offset="1" stop-color="#04060c" stop-opacity=".92"/></linearGradient>
<linearGradient id="{self.gid('hairg')}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{hx(d['hair'])}"/><stop offset="1" stop-color="{hx(dark(d['hair'],.35))}"/></linearGradient>
<linearGradient id="{self.gid('outg')}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{hx(light(d['outfit'],.1))}"/><stop offset="1" stop-color="{hx(dark(d['outfit'],.4))}"/></linearGradient>''')
        self.add(f'<rect width="{W}" height="{H}" fill="url(#{self.gid("bg")})"/>')
        # giant faint name
        self.add(f'<text x="-10" y="520" font-family="Impact,\'Arial Black\',sans-serif" font-weight="900" font-style="italic" font-size="300" fill="none" stroke="{g}" stroke-opacity=".16" stroke-width="3" transform="rotate(-90 60 520) translate(-60 120)" textLength="760" lengthAdjust="spacingAndGlyphs">{d["name"]}</text>')
        # speed burst
        for i in range(34):
            a = i / 34 * math.tau + self.rnd.random() * .08; r0 = 150 + self.rnd.random() * 60; r1 = 600 + self.rnd.random() * 300; w = .012 + self.rnd.random() * .02
            x0, y0 = CX + math.cos(a) * r0, 400 + math.sin(a) * r0; x1, y1 = CX + math.cos(a - w) * r1, 400 + math.sin(a - w) * r1; x2, y2 = CX + math.cos(a + w) * r1, 400 + math.sin(a + w) * r1
            self.add(f'<path d="M{x0:.0f},{y0:.0f} L{x1:.0f},{y1:.0f} L{x2:.0f},{y2:.0f}Z" fill="{g2 if i%3==0 else g}" opacity="{.05+self.rnd.random()*.1:.2f}"/>')
        # halftone + diagonal slabs
        self.add(f'<rect x="0" y="560" width="{W}" height="440" fill="url(#{self.gid("dots")})" opacity=".35" style="mask-image:linear-gradient(0deg,#000,transparent)"/>')
        self.add(f'<polygon points="470,0 800,0 800,420 560,0" fill="{g}" opacity=".16"/><polygon points="0,700 0,420 270,1000 90,1000" fill="{g2}" opacity=".09"/>')
        self.add(f'<circle cx="{CX}" cy="420" r="330" fill="none" stroke="{g}" stroke-opacity=".5" stroke-width="3"/><circle cx="{CX}" cy="420" r="380" fill="none" stroke="{g2}" stroke-opacity=".25" stroke-width="1.5" stroke-dasharray="4 14"/><circle cx="{CX}" cy="420" r="270" fill="{g}" opacity=".18" filter="url(#{self.gid("blur")})"/>')

    # ------------------------------------------------------------------ body ----
    def body(self):
        d = self.d; gear = d['gear']; wide = d.get('wide', 1.0); oc = hx(d['outfit']); o2 = hx(d['o2']); acc = hx(d['acc']); sk = hx(d['skin'])
        sx = lambda x: CX + (x - CX) * wide
        # shoulders / torso
        gi = 'gi' in gear
        self.add(f'<path d="M{sx(95):.0f},1000 C{sx(105):.0f},800 {sx(215):.0f},700 {sx(330):.0f},664 L{sx(470):.0f},664 C{sx(585):.0f},700 {sx(695):.0f},800 {sx(705):.0f},1000Z" fill="url(#{self.gid("outg")})" stroke="{hx(dark(d["outfit"],.7))}" stroke-width="5" stroke-linejoin="round"/>')
        # neck
        self.add(f'<path d="M352,560 L352,650 C352,690 380,712 400,712 C420,712 448,690 448,650 L448,560Z" fill="{sk}"/><path d="M352,600 C380,640 420,640 448,600 L448,560 L352,560Z" fill="{hx(self.skinD)}" opacity=".7"/>')
        if gi:
            self.add(f'<path d="M{sx(300):.0f},664 L400,860 L{sx(500):.0f},664 L460,664 L400,780 L340,664Z" fill="{sk}"/><path d="M{sx(285):.0f},664 L400,880 L360,664Z" fill="{oc}" stroke="{hx(dark(d["outfit"],.7))}" stroke-width="4"/><path d="M{sx(515):.0f},664 L400,880 L440,664Z" fill="{hx(light(d["outfit"],.12))}" stroke="{hx(dark(d["outfit"],.7))}" stroke-width="4"/>')
        else:
            self.add(f'<path d="M352,664 L400,740 L448,664 L470,664 C460,700 430,780 400,800 C370,780 340,700 330,664Z" fill="{hx(dark(d["outfit"],.5))}"/>')
        if 'jacket' in gear or 'coat' in gear or 'haori' in gear:
            c2 = hx(light(d['outfit'], .08))
            self.add(f'<path d="M{sx(262):.0f},650 L352,640 L372,760 L330,1000 L{sx(210):.0f},1000 C{sx(220):.0f},840 {sx(240):.0f},720 {sx(262):.0f},650Z" fill="{c2}" stroke="{hx(dark(d["outfit"],.7))}" stroke-width="4"/><path d="M{sx(538):.0f},650 L448,640 L428,760 L470,1000 L{sx(590):.0f},1000 C{sx(580):.0f},840 {sx(560):.0f},720 {sx(538):.0f},650Z" fill="{c2}" stroke="{hx(dark(d["outfit"],.7))}" stroke-width="4"/>')
            self.add(f'<path d="M358,645 L330,600 L300,640 L330,700Z M442,645 L470,600 L500,640 L470,700Z" fill="{acc}" stroke="{hx(dark(d["outfit"],.7))}" stroke-width="4" stroke-linejoin="round"/>')
            self.add(f'<line x1="372" y1="760" x2="332" y2="1000" stroke="{acc}" stroke-width="7" opacity=".9"/><line x1="428" y1="760" x2="468" y2="1000" stroke="{acc}" stroke-width="7" opacity=".9"/>')
        if 'haori' in gear:
            self.add(f'<path d="M{sx(130):.0f},720 L{sx(60):.0f},1000 L{sx(200):.0f},1000Z M{sx(670):.0f},720 L{sx(740):.0f},1000 L{sx(600):.0f},1000Z" fill="{hx(light(d["outfit"],.15))}" opacity=".9"/>')
        if 'vest' in gear:
            self.add(f'<path d="M300,664 L360,664 L380,900 L{sx(250):.0f},1000 L{sx(170):.0f},1000 C{sx(190):.0f},820 {sx(250):.0f},720 300,664Z M500,664 L440,664 L420,900 L{sx(550):.0f},1000 L{sx(630):.0f},1000 C{sx(610):.0f},820 {sx(550):.0f},720 500,664Z" fill="{oc}" stroke="{hx(dark(d["outfit"],.7))}" stroke-width="4"/><path d="M340,664 Q400,740 460,664 L460,1000 L340,1000Z" fill="{sk}"/><path d="M340,760 Q400,830 460,760" fill="none" stroke="{hx(self.skinD)}" stroke-width="5" opacity=".7"/>')
        if 'armor' in gear:
            self.add(f'<ellipse cx="{sx(170):.0f}" cy="740" rx="115" ry="80" fill="{hx(0x8b97ad)}" stroke="{hx(0x1b2030)}" stroke-width="6"/><ellipse cx="{sx(630):.0f}" cy="740" rx="115" ry="80" fill="{hx(0x8b97ad)}" stroke="{hx(0x1b2030)}" stroke-width="6"/><path d="M{sx(80):.0f},730 Q{sx(170):.0f},690 {sx(260):.0f},735" fill="none" stroke="{acc}" stroke-width="12"/><path d="M{sx(540):.0f},735 Q{sx(630):.0f},690 {sx(720):.0f},730" fill="none" stroke="{acc}" stroke-width="12"/>')
            self.add(f'<path d="M{sx(280):.0f},680 Q400,740 {sx(520):.0f},680 L{sx(540):.0f},1000 L{sx(260):.0f},1000Z" fill="{hx(0x7b87a0)}" stroke="{hx(0x1b2030)}" stroke-width="6"/><circle cx="400" cy="800" r="42" fill="{hx(d["glow"])}" filter="url(#{self.gid("blur2")})"/><circle cx="400" cy="800" r="26" fill="{hx(d["glow2"])}"/><rect x="{sx(300):.0f}" y="900" width="{(sx(500)-sx(300)):.0f}" height="26" fill="{acc}"/>')
        if 'xemblem' in gear:
            gg = hx(d['glow']); self.add(f'<g stroke="{hx(d["glow2"])}" stroke-width="12" stroke-linecap="round" filter="url(#{self.gid("blur2")})" opacity=".95"><line x1="365" y1="830" x2="435" y2="920"/><line x1="435" y1="830" x2="365" y2="920"/></g><g stroke="#fff" stroke-width="5" stroke-linecap="round"><line x1="365" y1="830" x2="435" y2="920"/><line x1="435" y1="830" x2="365" y2="920"/></g>')
        if 'beads' in gear:
            for i in range(13):
                a = i / 12 * math.pi; x = 400 + math.cos(a + math.pi) * 78 * -1; y = 690 + math.sin(a) * 95
                self.add(f'<circle cx="{400+math.cos(a)*84:.0f}" cy="{668+math.sin(a)*88:.0f}" r="{13 if i%3 else 17}" fill="{hx(d["glow"]) if i%3==0 else acc}" stroke="{hx(dark(d["hair"],.6))}" stroke-width="3"/>')
        if 'scarfshort' in gear or 'scarf' in gear:
            self.add(f'<path d="M300,650 Q400,720 500,650 L520,700 Q400,780 280,700Z" fill="{acc}" stroke="{hx(dark(d["acc"],.6))}" stroke-width="4"/>')
            if 'scarf' in gear: self.add(f'<path d="M470,700 Q560,780 520,900 Q560,960 520,1000 L600,1000 Q640,900 580,780Z" fill="{acc}" stroke="{hx(dark(d["acc"],.6))}" stroke-width="4"/>')
        if 'headset' in gear:
            pass
        # shoulder rim light
        self.add(f'<path d="M{sx(705):.0f},1000 C{sx(695):.0f},800 {sx(585):.0f},700 {sx(470):.0f},664" fill="none" stroke="{hx(d["glow"])}" stroke-width="6" opacity=".9" filter="url(#{self.gid("blur2")})"/>')
        if 'claws' in gear or 'katana' in gear:
            pass

    # ------------------------------------------------------------------ face ----
    def face_path(self):
        w = self.d.get('wide', 1.0); j = 1 if not self.d.get('fem') else .93
        def X(x): return CX + (x - CX) * w * (1 if abs(x-CX) < 100 else 1)
        return (f'M{X(250):.0f},410 C{X(250):.0f},300 {X(318):.0f},252 400,252 C{X(482):.0f},252 {X(550):.0f},300 {X(550):.0f},410 '
                f'C{X(550):.0f},472 {X(522):.0f},532 {X(474):.0f},574 C{X(440):.0f},602 {420:.0f},612 400,614 C380,612 {X(360):.0f},602 {X(326):.0f},574 C{X(278):.0f},532 {X(250):.0f},472 {X(250):.0f},410Z')

    def eye(self, side):
        d = self.d; fem = d.get('fem'); cx = 400 + side * 80; cy = 448; e = d['eye']; ed = dark(e, .55); el = light(e, .55); i = self.gid(f'eye{side+1}')
        sc = 1.08 if fem else 1.0
        self.defs.append(f'<clipPath id="{i}c"><path d="M-54,0 C-46,-56 36,-66 58,-8 C52,36 -34,46 -54,0Z"/></clipPath><linearGradient id="{i}g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{hx(ed)}"/><stop offset=".5" stop-color="{hx(e)}"/><stop offset="1" stop-color="{hx(el)}"/></linearGradient>')
        t = f'translate({cx},{cy}) scale({-side*sc},{sc})'  # outer corner on -x side for the viewer's left eye
        s = f'<g transform="{t}">'
        s += '<path d="M-54,0 C-46,-56 36,-66 58,-8 C52,36 -34,46 -54,0Z" fill="#fff"/>'
        s += f'<g clip-path="url(#{i}c)"><ellipse cx="6" cy="2" rx="37" ry="50" fill="url(#{i}g)"/><ellipse cx="6" cy="-4" rx="37" ry="22" fill="{hx(ed)}" opacity=".55"/><ellipse cx="6" cy="2" rx="15" ry="26" fill="#0b0c14"/>'
        s += f'<ellipse cx="-8" cy="-20" rx="11" ry="14" fill="#fff"/><circle cx="18" cy="20" r="6" fill="#fff" opacity=".95"/><circle cx="-18" cy="14" r="3" fill="#fff" opacity=".7"/><ellipse cx="6" cy="34" rx="22" ry="10" fill="{hx(el)}" opacity=".55"/></g>'
        s += '<path d="M-60,2 C-50,-62 38,-72 62,-8" fill="none" stroke="#0a0b12" stroke-width="11" stroke-linecap="round"/>'
        s += '<path d="M-62,0 L-80,-18" stroke="#0a0b12" stroke-width="8" stroke-linecap="round"/>'
        if fem: s += '<path d="M-56,-22 L-72,-40 M-44,-40 L-54,-60" stroke="#0a0b12" stroke-width="5" stroke-linecap="round"/>'
        s += f'<path d="M-50,8 C-34,42 30,44 52,-4" fill="none" stroke="{hx(self.skinDD)}" stroke-width="3" opacity=".6"/>'
        s += f'<path d="M-52,-14 C-34,-74 40,-82 64,-18" fill="none" stroke="{hx(self.skinD)}" stroke-width="3.5" opacity=".7"/></g>'
        self.add(s)

    def face(self):
        d = self.d; sk = hx(d['skin']); w = d.get('wide', 1.0); fp = self.face_path()
        # ears
        for sd in (-1, 1): self.add(f'<ellipse cx="{CX+sd*158*w:.0f}" cy="455" rx="24" ry="44" fill="{sk}" stroke="{hx(self.skinD)}" stroke-width="3"/>')
        self.add(f'<path d="{fp}" fill="{sk}"/>')
        # shading (light from upper-left)
        self.defs.append(f'<clipPath id="{self.gid("fc")}"><path d="{fp}"/></clipPath>')
        self.add(f'<g clip-path="url(#{self.gid("fc")})"><path d="M520,250 C600,330 570,520 440,640 L700,640 L700,250Z" fill="{hx(self.skinD)}" opacity=".5"/><ellipse cx="400" cy="660" rx="170" ry="70" fill="{hx(self.skinDD)}" opacity=".35"/><ellipse cx="318" cy="530" rx="46" ry="22" fill="#ff7a8a" opacity=".22"/><ellipse cx="482" cy="530" rx="46" ry="22" fill="#ff7a8a" opacity=".22"/></g>')
        # brows
        for sd in (-1, 1):
            bx = CX + sd * 80; tilt = d['brow'] * 38
            y_in = 372 + tilt * .6; y_out = 372 - tilt * .2 - 4
            xi = CX + sd * 30; xo = CX + sd * 130
            self.add(f'<path d="M{xi:.0f},{y_in:.0f} Q{(xi+xo)/2:.0f},{y_in-14-tilt*.2:.0f} {xo:.0f},{y_out:.0f} Q{(xi+xo)/2:.0f},{y_in-4:.0f} {xi:.0f},{y_in+8:.0f}Z" fill="{hx(self.hairD)}"/>')
        self.eye(-1); self.eye(1)
        # nose + mouth
        self.add(f'<path d="M398,520 Q404,530 396,534" fill="none" stroke="{hx(self.skinDD)}" stroke-width="4" stroke-linecap="round" opacity=".8"/>')
        if 'mask' not in d['gear']:
            smirk = 'M368,566 Q398,580 432,560' if not d.get('fem') else 'M372,566 Q400,584 428,566'
            self.add(f'<path d="{smirk}" fill="none" stroke="#3a1820" stroke-width="5" stroke-linecap="round"/><path d="M372,568 Q400,582 428,566" fill="none" stroke="{hx(self.skinD)}" stroke-width="0"/>')
            self.add(f'<path d="M382,576 Q400,590 420,572" fill="none" stroke="{hx(self.skinDD)}" stroke-width="2" opacity=".5"/>')
        if 'claws' in d['gear'] or d['style'] == 'spiky' and self.s == 'toxic-fang':
            self.add(f'<path d="M285,500 L335,512 M285,520 L330,526" stroke="{hx(d["glow"])}" stroke-width="3" opacity=".0"/>')
        # mask
        if 'mask' in d['gear']:
            self.add(f'<path d="M262,500 C300,510 350,505 400,500 C450,505 500,510 538,500 C528,560 480,614 400,622 C320,614 272,560 262,500Z" fill="#14111f" stroke="#05040a" stroke-width="5"/><path d="M300,540 L500,540" stroke="{hx(d["glow"])}" stroke-width="5" filter="url(#{self.gid("blur2")})"/><path d="M300,540 L500,540" stroke="{hx(d["glow2"])}" stroke-width="2.5"/>')
        # face rim light (right side)
        self.add(f'<path d="M545,380 C552,450 530,520 480,570" fill="none" stroke="{hx(light(d["glow"],.3))}" stroke-width="6" opacity=".8" filter="url(#{self.gid("blur2")})"/>')

    # ------------------------------------------------------------------ hair ----
    def hair_back(self):
        d = self.d; st = d['style']; hg = f'url(#{self.gid("hairg")})'; stroke = f'stroke="{hx(dark(d["hair"],.7))}" stroke-width="5" stroke-linejoin="round"'
        if st == 'long':
            self.add(f'<path d="M232,400 C190,520 170,760 150,1000 L650,1000 C630,760 610,520 568,400 C560,280 480,220 400,220 C320,220 240,280 232,400Z" fill="{hg}" {stroke}/>')
        if st == 'twin':
            for sd in (-1, 1):
                x0 = CX + sd * 150
                self.add(f'<path d="M{x0},330 C{CX+sd*330},330 {CX+sd*400},560 {CX+sd*330},760 C{CX+sd*300},880 {CX+sd*340},960 {CX+sd*300},1000 C{CX+sd*230},900 {CX+sd*190},780 {CX+sd*220},640 C{CX+sd*230},520 {CX+sd*190},420 {x0},400Z" fill="{hg}" {stroke}/>')
        if st == 'ponytail':
            self.add(f'<path d="M470,260 C600,170 760,230 740,380 C730,480 650,560 690,700 C650,640 620,520 640,420 C650,340 560,300 470,330Z" fill="{hg}" {stroke}/>')
        if st == 'crop' or st == 'messy' or st == 'topknot':
            self.add(f'<path d="M240,430 C220,290 300,225 400,225 C500,225 580,290 560,430 L560,480 L240,480Z" fill="{hg}" {stroke}/>')
    def hair_front(self):
        d = self.d; st = d['style']; hg = f'url(#{self.gid("hairg")})'; stroke = f'stroke="{hx(dark(d["hair"],.7))}" stroke-width="4.5" stroke-linejoin="round"'; hi = hx(d['hi']); w = d.get('wide', 1.0)
        X = lambda x: CX + (x - CX) * w
        def lock(bx, by, tx, ty, wd, c=.18): self.add(blade(X(bx), by, X(tx), ty, wd, c, hg, stroke))
        # spikes behind the cap
        if st == 'spiky':
            k = d.get('spikes', 1.0); sw = d.get('sweep', .2)
            for th, ln in [(-98, 130), (-76, 175), (-54, 205), (-30, 240), (-8, 270), (14, 250), (36, 220), (58, 190), (80, 160), (100, 120)]:
                a = math.radians(th); bx = 400 + 150 * math.sin(a) * w; by = 390 - 140 * math.cos(a)
                dx = math.sin(a) + sw; dy = -math.cos(a) * 1.0 - .15; l = math.hypot(dx, dy)
                self.add(blade(bx, by + 20, bx + dx / l * ln * k, by + 20 + dy / l * ln * k, 76, .12 * (1 if th < 0 else -1), hg, stroke))
        if st == 'messy':
            for th, ln in [(-95, 90), (-70, 120), (-45, 140), (-20, 150), (5, 150), (30, 140), (55, 125), (80, 105)]:
                a = math.radians(th); bx = 400 + 150 * math.sin(a); by = 390 - 140 * math.cos(a); dx = math.sin(a) * 1.2; dy = -math.cos(a) * .9
                l = math.hypot(dx, dy) or 1; self.add(blade(bx, by + 20, bx + dx / l * ln, by + 20 + dy / l * ln, 62, .2, hg, stroke))
        if st == 'crop':
            for th, ln in [(-80, 55), (-55, 70), (-30, 80), (-8, 85), (16, 80), (40, 72), (64, 62)]:
                a = math.radians(th); bx = 400 + 150 * math.sin(a) * w; by = 390 - 140 * math.cos(a); self.add(blade(bx, by + 20, bx + math.sin(a) * ln * 1.2, by + 20 - math.cos(a) * ln, 56, .1, hg, stroke))
        if st == 'topknot':
            self.add(f'<ellipse cx="400" cy="205" rx="64" ry="60" fill="{hg}" {stroke}/><rect x="366" y="240" width="68" height="40" rx="10" fill="{hx(d["acc"])}" stroke="{hx(dark(d["acc"],.6))}" stroke-width="4"/><ellipse cx="385" cy="190" rx="22" ry="14" fill="{hi}" opacity=".6"/>')
        # cap (hairline)
        self.add(f'<path d="M244,445 C222,296 300,226 400,226 C500,226 578,296 556,445 L536,400 C528,352 478,324 400,322 C322,324 272,352 264,400Z" fill="{hg}" {stroke}/>')
        # bangs
        centre = [(300, 336, 288, 432, 64), (345, 328, 338, 392, 52), (400, 322, 412, 452, 64), (455, 328, 470, 394, 52), (500, 336, 520, 438, 66)]
        if st in ('long', 'twin', 'ponytail'): centre = [(292, 340, 268, 470, 70), (350, 326, 356, 424, 62), (410, 322, 400, 398, 60), (462, 328, 476, 420, 62), (508, 340, 536, 470, 70)]
        if st in ('crop', 'topknot'): centre = [(310, 336, 300, 388, 52), (400, 322, 400, 380, 70), (490, 336, 500, 388, 52)]
        for bx, by, tx, ty, wd in centre: lock(bx, by, tx, ty, wd, .14)
        # side locks
        sl = {'long': 360, 'twin': 330, 'ponytail': 330, 'spiky': 300, 'messy': 300, 'crop': 250, 'topknot': 250}[st]
        for sd in (-1, 1): self.add(blade(CX + sd * 150 * w, 360, CX + sd * 168 * w, 360 + sl, 62, .08 * sd, hg, stroke))
        # shine band + highlights
        self.add(f'<path d="M290,330 C320,290 480,290 510,330" fill="none" stroke="{hi}" stroke-width="12" stroke-linecap="round" opacity=".55"/>')
        for sd in (-1, 1): self.add(f'<path d="M{CX+sd*60},{250} Q{CX+sd*110},{300} {CX+sd*125},{360}" fill="none" stroke="{hi}" stroke-width="6" stroke-linecap="round" opacity=".45"/>')
        # tie accents
        if st == 'twin':
            for sd in (-1, 1):
                self.add(f'<circle cx="{CX+sd*168}" cy="345" r="26" fill="{hx(d["acc"])}" stroke="{hx(dark(d["acc"],.6))}" stroke-width="4"/><circle cx="{CX+sd*168}" cy="345" r="12" fill="{hx(d["glow2"])}" filter="url(#{self.gid("blur2")})"/>')
        if st == 'ponytail': self.add(f'<ellipse cx="556" cy="320" rx="22" ry="30" fill="{hx(d["acc"])}" stroke="{hx(dark(d["acc"],.6))}" stroke-width="4" transform="rotate(30 556 320)"/>')

    def accessories(self):
        d = self.d; g = d['gear']; acc = hx(d['acc']); gl = hx(d['glow']); gl2 = hx(d['glow2']); dk = '#12141e'
        if 'headband' in g:
            self.add(f'<path d="M246,352 C300,326 500,326 554,352 L558,392 C500,366 300,366 242,392Z" fill="{acc}" stroke="{hx(dark(d["acc"],.6))}" stroke-width="5"/><path d="M552,380 Q640,420 620,520 Q660,430 560,360Z" fill="{acc}" stroke="{hx(dark(d["acc"],.6))}" stroke-width="4"/>')
            if self.s == 'titan': self.add(f'<rect x="372" y="335" width="56" height="38" rx="6" fill="{hx(0x8b97ad)}" stroke="#1b2030" stroke-width="4"/><path d="M386,345 l28,18 m0,-18 l-28,18" stroke="{gl}" stroke-width="4"/>')
        if 'goggles' in g:
            self.add(f'<path d="M232,330 C300,296 500,296 568,330 L572,362 C500,330 300,330 228,362Z" fill="{dk}" stroke="#05060a" stroke-width="4"/>')
            for sd in (-1, 1): self.add(f'<circle cx="{CX+sd*75}" cy="300" r="48" fill="{dk}" stroke="#05060a" stroke-width="5"/><circle cx="{CX+sd*75}" cy="300" r="35" fill="{gl2}"/><circle cx="{CX+sd*75}" cy="300" r="35" fill="{gl}" opacity=".5"/><path d="M{CX+sd*75-20},{288} Q{CX+sd*75},{268} {CX+sd*75+20},{282}" stroke="#fff" stroke-width="5" fill="none" opacity=".8" stroke-linecap="round"/>')
        if 'visor' in g:
            self.add(f'<path d="M238,356 C300,318 500,318 562,356 L558,386 C500,352 300,352 242,386Z" fill="{dk}" stroke="#05060a" stroke-width="4"/><path d="M246,368 C300,336 500,336 554,368" fill="none" stroke="{gl}" stroke-width="12" filter="url(#{self.gid("blur2")})"/><path d="M246,368 C300,336 500,336 554,368" fill="none" stroke="{gl2}" stroke-width="6" stroke-linecap="round"/>')
            for sd in (-1, 1): self.add(f'<rect x="{CX+sd*165-14}" y="425" width="28" height="70" rx="12" fill="{dk}" stroke="#05060a" stroke-width="4"/><circle cx="{CX+sd*165}" cy="460" r="8" fill="{gl}" filter="url(#{self.gid("blur2")})"/>')
        if 'headset' in g:
            self.add(f'<path d="M236,430 C216,250 330,200 400,200 C470,200 584,250 564,430" fill="none" stroke="{dk}" stroke-width="16" stroke-linecap="round"/><path d="M236,430 C216,250 330,200 400,200 C470,200 584,250 564,430" fill="none" stroke="{acc}" stroke-width="5" stroke-linecap="round"/>')
            for sd in (-1, 1): self.add(f'<rect x="{CX+sd*168-26}" y="410" width="52" height="90" rx="22" fill="{acc}" stroke="#05060a" stroke-width="5"/><rect x="{CX+sd*168-14}" y="428" width="28" height="54" rx="12" fill="{gl}"/><rect x="{CX+sd*168-14}" y="428" width="28" height="54" rx="12" fill="{gl2}" opacity=".5" filter="url(#{self.gid("blur2")})"/>')
            self.add(f'<path d="M{CX-168},498 Q{CX-150},560 {CX-60},572" fill="none" stroke="{dk}" stroke-width="7" stroke-linecap="round"/><circle cx="{CX-58}" cy="572" r="11" fill="{acc}" stroke="#05060a" stroke-width="3"/>')

    # -------------------------------------------------------------- effects ----
    def fx(self, phase='back'):
        d = self.d; fx = d['fx']; g = hx(d['glow']); g2 = hx(d['glow2']); r = self.rnd; blur = f'filter="url(#{self.gid("blur2")})"'
        pts = [(r.uniform(40, 760), r.uniform(80, 900)) for _ in range(26)]
        if phase == 'back': self._fxback(d, fx, g, g2, r, blur, pts); return
        self._fxfront(d, g, g2, r)

    def _fxback(self, d, fx, g, g2, r, blur, pts):
        if fx in ('flame',):
            for x, y in pts:
                s = r.uniform(3, 9); self.add(f'<path d="M{x:.0f},{y-s*2:.0f} Q{x+s:.0f},{y:.0f} {x:.0f},{y+s:.0f} Q{x-s:.0f},{y:.0f} {x:.0f},{y-s*2:.0f}Z" fill="{g2 if r.random()<.5 else g}" opacity="{r.uniform(.5,.95):.2f}" {blur if r.random()<.2 else ""}/>')
        elif fx == 'ice':
            for x, y in pts:
                s = r.uniform(5, 16); self.add(f'<path d="M{x:.0f},{y-s:.0f} L{x+s*.6:.0f},{y:.0f} L{x:.0f},{y+s:.0f} L{x-s*.6:.0f},{y:.0f}Z" fill="{g2}" opacity="{r.uniform(.4,.9):.2f}"/>')
        elif fx in ('spark',):
            for i in range(7):
                x, y = r.uniform(40, 760), r.uniform(100, 800); pts2 = [(x, y)]
                for _ in range(5): x += r.uniform(-40, 40); y += r.uniform(15, 55); pts2.append((x, y))
                p = ' '.join(f'{a:.0f},{b:.0f}' for a, b in pts2); self.add(f'<polyline points="{p}" fill="none" stroke="{g}" stroke-width="7" opacity=".7" {blur}/><polyline points="{p}" fill="none" stroke="#fff" stroke-width="2.5" opacity=".95"/>')
        elif fx in ('void', 'storm'):
            for i in range(9):
                y = r.uniform(120, 880); x = r.uniform(-50, 600); l = r.uniform(120, 320); self.add(f'<path d="M{x:.0f},{y:.0f} Q{x+l/2:.0f},{y-30:.0f} {x+l:.0f},{y+r.uniform(-20,20):.0f}" fill="none" stroke="{g2 if i%2 else g}" stroke-width="{r.uniform(2,5):.1f}" opacity="{r.uniform(.3,.7):.2f}" stroke-linecap="round"/>')
            for x, y in pts[:12]: self.add(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r.uniform(2,6):.1f}" fill="{g2}" opacity=".7"/>')
        elif fx == 'quake':
            for x, y in pts[:14]:
                s = r.uniform(6, 22); self.add(f'<polygon points="{x:.0f},{y-s:.0f} {x+s:.0f},{y-s*.2:.0f} {x+s*.5:.0f},{y+s:.0f} {x-s:.0f},{y+s*.4:.0f}" fill="{hx(0x6b7488)}" stroke="{g}" stroke-width="2" opacity=".85"/>')
        elif fx == 'cyber':
            for i in range(14):
                x, y = r.uniform(30, 760), r.uniform(80, 900); self.add(f'<rect x="{x:.0f}" y="{y:.0f}" width="{r.uniform(18,70):.0f}" height="3" fill="{g}" opacity=".6"/><rect x="{x:.0f}" y="{y+8:.0f}" width="{r.uniform(8,30):.0f}" height="3" fill="{g2}" opacity=".6"/>')
            for x, y in pts[:6]: self.add(f'<polygon points="{" ".join(f"{x+math.cos(k*1.047)*14:.0f},{y+math.sin(k*1.047)*14:.0f}" for k in range(6))}" fill="none" stroke="{g}" stroke-width="2" opacity=".7"/>')
        elif fx == 'glitch':
            for i in range(12):
                x, y = r.uniform(20, 720), r.uniform(80, 900); s = r.uniform(10, 34); c = g if i % 2 else g2; self.add(f'<rect x="{x:.0f}" y="{y:.0f}" width="{s:.0f}" height="{s:.0f}" fill="none" stroke="{c}" stroke-width="3" opacity=".8"/><rect x="{x+5:.0f}" y="{y+4:.0f}" width="{s:.0f}" height="{s:.0f}" fill="{c}" opacity=".18"/>')
            for i in range(5): y = r.uniform(300, 700); self.add(f'<rect x="0" y="{y:.0f}" width="800" height="{r.uniform(3,9):.0f}" fill="{g2}" opacity=".08"/>')
        else:  # jade / venom
            for x, y in pts:
                s = r.uniform(4, 14); self.add(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{s:.0f}" fill="{g}" opacity=".25"/><circle cx="{x:.0f}" cy="{y:.0f}" r="{s*.45:.1f}" fill="{g2}" opacity=".9"/>')
    def _fxfront(self, d, g, g2, r):
        gear = d['gear']
        if 'katana' in gear: self.add(f'<g transform="rotate(14 650 520)"><rect x="640" y="150" width="22" height="700" fill="#cfd8e8" stroke="#10141f" stroke-width="4"/><rect x="654" y="150" width="8" height="700" fill="{g2}"/><rect x="620" y="840" width="62" height="16" fill="{hx(d["acc"])}" stroke="#10141f" stroke-width="3"/><rect x="643" y="856" width="16" height="140" fill="#161a28"/></g>')
        if 'claws' in gear:
            for i, x in enumerate((90, 130, 170)): self.add(f'<path d="M{x},940 L{x+14},760 L{x+32},940Z" fill="{g}" opacity=".9" stroke="#fff" stroke-width="1.5"/>')
        # sparkles
        for _ in range(7):
            x, y = r.uniform(60, 740), r.uniform(100, 700); s = r.uniform(8, 20)
            self.add(f'<path d="M{x:.0f},{y-s:.0f} Q{x:.0f},{y:.0f} {x+s:.0f},{y:.0f} Q{x:.0f},{y:.0f} {x:.0f},{y+s:.0f} Q{x:.0f},{y:.0f} {x-s:.0f},{y:.0f} Q{x:.0f},{y:.0f} {x:.0f},{y-s:.0f}Z" fill="#fff" opacity=".85"/>')

    def render(self):
        self.background(); self.fx('back'); self.hair_back(); self.body(); self.face(); self.hair_front(); self.accessories(); self.fx('front')
        self.add(f'<rect width="{W}" height="{H}" fill="url(#{self.gid("fade")})"/>')
        # border accents
        self.add(f'<rect x="10" y="10" width="780" height="980" fill="none" stroke="{hx(self.d["glow"])}" stroke-opacity=".35" stroke-width="2"/><path d="M10,60 L10,10 L60,10 M790,940 L790,990 L740,990" fill="none" stroke="{hx(self.d["glow2"])}" stroke-width="5"/>')
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><defs>{"".join(self.defs)}</defs>{"".join(self.o)}</svg>'

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'out'; os.makedirs(out, exist_ok=True)
    for s in R:
        open(f'{out}/{s}.svg', 'w').write(P(s).render())
    print('ok', len(R))
