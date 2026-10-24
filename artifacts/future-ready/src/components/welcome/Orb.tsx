import { useEffect, useRef, useState } from 'react';

const vertex = `attribute vec2 position;
void main(){ gl_Position=vec4(position,0.,1.); }`;
const fragment = `precision highp float;
uniform vec2 resolution; uniform float time;
mat3 rotateY(float a){float c=cos(a),s=sin(a);return mat3(c,0.,s,0.,1.,0.,-s,0.,c);}
mat3 rotateZ(float a){float c=cos(a),s=sin(a);return mat3(c,s,0.,-s,c,0.,0.,0.,1.);}
float hash(vec3 p){return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453);}
float noise(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
 return mix(mix(mix(hash(i),hash(i+vec3(1,0,0)),f.x),mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y),f.z);}
float fbm(vec3 p){float n=0.,a=.5;for(int i=0;i<4;i++){n+=a*noise(p);p=p*2.03+vec3(4.7,1.2,8.1);a*=.5;}return n;}
void main(){
 vec2 uv=(gl_FragCoord.xy-.5*resolution)/min(resolution.x,resolution.y)*2.65;
 float r=length(uv),angle=atan(uv.y,uv.x);
 vec3 blue=vec3(.13,.48,.88),orange=vec3(1.,.29,.075);
 float side=.5+.5*sin(angle-1.1);
 vec3 rimColor=mix(blue,orange,smoothstep(.25,.8,side));
 float halo=exp(-abs(r-1.)*18.)*.23+exp(-abs(r-1.)*5.)*.07;
 vec3 color=rimColor*halo;
 if(r<1.){
  vec3 n=vec3(uv,sqrt(1.-r*r));
  vec3 p=rotateZ(-.45)*rotateY(time*.24)*n;
  float cloud=fbm(p*3.2+vec3(0.,time*.035,0.));
  float flow=p.y*6.5+p.x*2.2+cloud*5.5;
  float ribbons=pow(.5+.5*sin(flow*3.4),14.);
  float fine=pow(.5+.5*sin(flow*10.+fbm(p*9.)*3.),26.);
  float fresnel=pow(1.-n.z,2.2);
  vec3 light=normalize(vec3(-.6,.6,1.));
  float diffuse=max(0.,dot(n,light));
  float movingSpec=pow(max(0.,dot(normalize(n+(cloud-.5)*.15),normalize(vec3(.45*sin(time*.16),.65,1.)))),60.);
  vec3 glass=mix(vec3(.012,.032,.055),vec3(.08,.18,.25),cloud)*(.5+diffuse*.7);
  float tint=.5+.5*sin(p.x*3.4+p.z*3.+time*.08);
  vec3 energy=mix(blue,orange,smoothstep(.48,.73,tint));
  color+=glass+energy*(ribbons*.36+fine*.10)*(fresnel*.9+.15);
  color+=rimColor*(pow(fresnel,3.)*2.1+pow(fresnel,.7)*.11);
  color+=mix(vec3(.30,.67,1.),vec3(1.,.87,.70),side)*movingSpec*.95;
  float arc=exp(-pow((r-.87)*34.,2.))*(.5+.5*sin(angle*2.+cloud*6.+time*.13));
  color+=energy*arc*.27;
  color+=vec3(.4,.65,.8)*pow(max(0.,dot(n,normalize(vec3(-.6,-.5,.1)))),18.)*.6;
 }
 // A thin, oblique light trail behind the sphere, without any hand imagery.
 float streak=exp(-abs(uv.y+uv.x*.43+.12)*50.)*exp(-r*.7)*smoothstep(.98,1.2,r);
 color+=mix(orange,blue,smoothstep(-.8,.9,uv.x))*streak*.13;
 color=vec3(1.)-exp(-color*1.45);
 gl_FragColor=vec4(color,1.);
}`;

export function Orb({ paused }: { paused: boolean }) {
  const ref = useRef<HTMLCanvasElement>(null);
  const elapsed = useRef(0);
  const [fallback, setFallback] = useState(false);
  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const gl = canvas.getContext('webgl', { alpha: false, antialias: false, powerPreference: 'low-power' });
    if (!gl) { setFallback(true); return; }
    function compile(type: number, source: string) {
      const shader = gl!.createShader(type)!;
      gl!.shaderSource(shader, source); gl!.compileShader(shader);
      if (!gl!.getShaderParameter(shader, gl!.COMPILE_STATUS)) { gl!.deleteShader(shader); return null; }
      return shader;
    }
    const vs = compile(gl.VERTEX_SHADER, vertex), fs = compile(gl.FRAGMENT_SHADER, fragment);
    if (!vs || !fs) { if (vs) gl.deleteShader(vs); if (fs) gl.deleteShader(fs); setFallback(true); return; }
    const program = gl.createProgram()!;
    gl.attachShader(program, vs); gl.attachShader(program, fs); gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      gl.deleteProgram(program); gl.deleteShader(vs); gl.deleteShader(fs); setFallback(true); return;
    }
    gl.useProgram(program);
    const buffer = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]), gl.STATIC_DRAW);
    const pos = gl.getAttribLocation(program, 'position'); gl.enableVertexAttribArray(pos); gl.vertexAttribPointer(pos, 2, gl.FLOAT, false, 0, 0);
    const uResolution = gl.getUniformLocation(program, 'resolution'), uTime = gl.getUniformLocation(program, 'time');
    let frame = 0, activeTime = elapsed.current, lastTime = 0, lost = false;
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const draw = () => {
      if (lost) return;
      gl.viewport(0, 0, canvas.width, canvas.height); gl.uniform2f(uResolution, canvas.width, canvas.height);
      gl.uniform1f(uTime, 8 + activeTime / 1000); gl.drawArrays(gl.TRIANGLES, 0, 6);
    };
    const tick = (now: number) => {
      if (lastTime) activeTime += Math.min(now-lastTime, 60);
      lastTime = now; draw(); frame = requestAnimationFrame(tick);
    };
    const update = () => {
      cancelAnimationFrame(frame); lastTime = 0;
      if (!paused && !motion.matches && !document.hidden && !lost) frame = requestAnimationFrame(tick);
      else draw();
    };
    const resize = () => {
      const size = Math.min(850, Math.round(canvas.clientWidth * Math.min(devicePixelRatio, 1.5)));
      canvas.width = size; canvas.height = size; draw();
    };
    const loss = (event: Event) => { event.preventDefault(); lost = true; cancelAnimationFrame(frame); setFallback(true); };
    const observer = new ResizeObserver(resize); observer.observe(canvas); resize(); update();
    motion.addEventListener('change', update); document.addEventListener('visibilitychange', update); canvas.addEventListener('webglcontextlost', loss);
    return () => {
      elapsed.current = activeTime;
      cancelAnimationFrame(frame); observer.disconnect(); motion.removeEventListener('change', update);
      document.removeEventListener('visibilitychange', update); canvas.removeEventListener('webglcontextlost', loss);
      gl.deleteBuffer(buffer); gl.deleteProgram(program); gl.deleteShader(vs); gl.deleteShader(fs);
    };
  }, [paused]);
  return <div className={`orb-stage ${fallback ? 'orb-fallback' : ''}`} aria-hidden="true"><canvas ref={ref} className="orb-canvas" /></div>;
}
