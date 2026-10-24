import { useEffect, useRef } from 'react';

export const ENTRANCE_TIMING = { assemble: 1400, hold: 500, scatter: 650 } as const;
type Particle = { x: number; y: number; sx: number; sy: number; dx: number; dy: number; size: number; alpha: number };

export function ParticleEntrance({ onComplete }: { onComplete: () => void }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const layerRef = useRef<HTMLDivElement>(null);
  const skipRef = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    skipRef.current?.focus();
    const canvas = canvasRef.current!, layer = layerRef.current!;
    const ctx = canvas.getContext('2d');
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (!ctx || reduced.matches) {
      layer.dataset.phase = 'hold'; layer.classList.add('static-entrance');
      const timer = window.setTimeout(onComplete, ENTRANCE_TIMING.hold);
      return () => clearTimeout(timer);
    }
    let w = 0, h = 0, particles: Particle[] = [], frame = 0, last = 0, elapsed = 0;
    // Seeded visual layout, independent of any user information.
    let seed = 43;
    const random = () => { seed=(seed*1664525+1013904223)>>>0; return seed/4294967296; };
    const resize = () => {
      w = window.innerWidth; h = window.innerHeight;
      const dpr = Math.min(devicePixelRatio, 2);
      canvas.width = w*dpr; canvas.height = h*dpr; ctx.setTransform(dpr,0,0,dpr,0,0);
      const mask = document.createElement('canvas'); mask.width=w; mask.height=h;
      const c = mask.getContext('2d')!;
      let size = Math.min(160, w*.135);
      c.font=`700 ${size}px Arial, sans-serif`;
      size *= Math.min(1, w*.82/c.measureText('Future Ready').width);
      c.font=`700 ${size}px Arial, sans-serif`; c.textAlign='center'; c.textBaseline='middle'; c.fillStyle='white';
      c.fillText('Future Ready',w/2,h/2);
      const pixels=c.getImageData(0,0,w,h).data;
      particles=[]; seed=43;
      const step = w<600 ? 3 : 4;
      for(let y=Math.floor(h/2-size);y<h/2+size;y+=step) for(let x=0;x<w;x+=step) {
        if(y<0||y>=h||pixels[(y*w+x)*4+3]<120) continue;
        const angle=random()*Math.PI*2, dist=Math.max(w,h)*(.45+random()*.65);
        particles.push({x:x+(random()-.5)*1.1,y:y+(random()-.5)*1.1,sx:random()*w,sy:random()*h,
          dx:Math.cos(angle)*dist,dy:Math.sin(angle)*dist,size:.65+random()*.85,alpha:.45+random()*.55});
      }
    };
    const {assemble,hold,scatter}=ENTRANCE_TIMING;
    const tick=(now:number)=>{
      if(last) elapsed+=now-last;
      last=now;
      ctx.fillStyle='#000';ctx.fillRect(0,0,w,h);
      const phase=elapsed<assemble?'assemble':elapsed<assemble+hold?'hold':'scatter';
      layer.dataset.phase=phase;
      const a=Math.min(1,elapsed/assemble), gather=1-Math.pow(1-a,3);
      const s=Math.max(0,Math.min(1,(elapsed-assemble-hold)/scatter));
      for(const p of particles){
        const x=phase==='assemble'?p.sx+(p.x-p.sx)*gather:p.x+p.dx*s*s;
        const y=phase==='assemble'?p.sy+(p.y-p.sy)*gather:p.y+p.dy*s*s;
        ctx.fillStyle=`rgba(255,255,255,${p.alpha*(1-s)*Math.min(1,a*4+.1)})`;
        ctx.beginPath();ctx.arc(x,y,p.size,0,Math.PI*2);ctx.fill();
      }
      if(elapsed>=assemble+hold+scatter){onComplete();return;}
      frame=requestAnimationFrame(tick);
    };
    const visibility=()=>{cancelAnimationFrame(frame);last=0;if(!document.hidden)frame=requestAnimationFrame(tick);};
    const motionChange=()=>{if(reduced.matches)onComplete();};
    resize();frame=requestAnimationFrame(tick);
    window.addEventListener('resize',resize);document.addEventListener('visibilitychange',visibility);reduced.addEventListener('change',motionChange);
    return()=>{cancelAnimationFrame(frame);window.removeEventListener('resize',resize);document.removeEventListener('visibilitychange',visibility);reduced.removeEventListener('change',motionChange);};
  }, [onComplete]);
  return <div className="particle-entrance" ref={layerRef} data-phase="assemble" role="dialog" aria-modal="true" aria-label="Entering Future Ready">
    <canvas ref={canvasRef} aria-hidden="true"/><span className="entrance-static-title" aria-hidden="true">Future Ready</span>
    <span className="sr-only" role="status">Opening the Future Ready demo.</span>
    <button className="entrance-skip" ref={skipRef} onClick={onComplete}>Skip animation <span aria-hidden="true">↗</span></button>
  </div>;
}
