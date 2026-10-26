// Landing-page preview: the same anime rig used in-game (KAITO-X), cycling idle -> combo poses.
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js';
import { Fighter } from '../game/fighter.js';
import { ROSTER } from '../game/roster.js';
import { STANCE, MOVES, clonePose, evalKeys, walkPose } from '../game/rig.js';
const host = document.querySelector('#hero-3d-preview');
if (host) {
  let renderer;
  try { renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'low-power' }); } catch (e) { host.textContent = '3D PREVIEW UNAVAILABLE'; }
  if (renderer) {
    const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(32, 1, .1, 60); camera.position.set(0, 1.9, 8.2); camera.lookAt(0, 1.45, 0);
    renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1.5)); renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.15; host.appendChild(renderer.domElement);
    scene.add(new THREE.HemisphereLight(0xa8c4ff, 0x1a1a2e, 1.6));
    const key = new THREE.DirectionalLight(0xfff4ea, 2.8); key.position.set(-2, 6, 6); scene.add(key);
    const rim = new THREE.DirectionalLight(0x6fd8ff, 2.2); rim.position.set(5, 3, -5); scene.add(rim);
    const data = ROSTER['cyber-x'], fighter = new Fighter(scene, data, { isPlayer: true });
    fighter.root.rotation.y = 0; fighter.viewYaw = -.55; fighter.root.position.y = -.02; fighter.setExpression('focus');
    const ring = new THREE.Mesh(new THREE.TorusGeometry(1.25, .016, 8, 72), new THREE.MeshBasicMaterial({ color: new THREE.Color(data.glow).multiplyScalar(1.6) })); ring.rotation.x = Math.PI / 2; ring.position.y = .05; scene.add(ring);
    const ring2 = new THREE.Mesh(new THREE.TorusGeometry(1.6, .01, 8, 72), new THREE.MeshBasicMaterial({ color: 0xff4a67, transparent: true, opacity: .5 })); ring2.rotation.set(Math.PI / 2, 0, 0); ring2.position.y = .05; scene.add(ring2);
    const clock = new THREE.Clock(), tmp = clonePose(STANCE), cycle = ['jab', 'cross', 'kick', 'cleave', 'dash'];
    let t = 0, idx = 0, mt = -2.4;
    const resize = () => { const w = Math.max(1, host.clientWidth), h = Math.max(1, host.clientHeight); camera.aspect = w / h; camera.updateProjectionMatrix(); renderer.setSize(w, h); };
    window.addEventListener('resize', resize); resize();
    (function frame() {
      requestAnimationFrame(frame); const dt = Math.min(clock.getDelta(), .05); t += dt; mt += dt;
      const mv = MOVES[cycle[idx]]; let pose;
      if (mt > 0 && mt <= mv.dur) { pose = evalKeys(mv.keys, mt, tmp); fighter.setExpression('attack'); }
      else { pose = walkPose(tmp, 0, 0); const b = Math.sin(t * 2.4) * .025; pose.chest[0] += b; pose.spine[0] += b * .6; pose.uaL[0] += b; pose.uaR[0] -= b; fighter.setExpression('focus'); if (mt > mv.dur + 1.1) { mt = 0; idx = (idx + 1) % cycle.length; } }
      fighter.trackPose(pose, dt, mt > 0 && mt <= mv.dur ? 40 : 12); fighter.normalizeSpin(); fighter.update(dt);
      fighter.viewYaw = -.55 + Math.sin(t * .5) * .25; ring.rotation.z = t * .3; ring2.rotation.y = t * .4; renderer.render(scene, camera);
    })();
  }
}
