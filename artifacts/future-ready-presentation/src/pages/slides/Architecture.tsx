export default function Architecture() {
  return (
    <div className="w-screen h-screen overflow-hidden relative bg-bg text-text font-body">
      <h1 className="absolute left-[6vw] top-[8vh] w-[88vw] text-[3.8vw] leading-[1.12] font-display font-extrabold tracking-tight">A transparent full-stack architecture</h1>
      <div className="absolute left-[6vw] right-[6vw] top-[30vh] flex flex-col gap-[3.6vh] text-[2vw] leading-[1.3]">
        <p className="border-b border-primary/30 pb-[2vh]"><strong className="text-primary font-extrabold">React + TypeScript + Vite</strong> for the interface</p>
        <p className="border-b border-primary/30 pb-[2vh]"><strong className="text-primary font-extrabold">WebGL/GLSL</strong> orb and Canvas 2D particle entrance</p>
        <p className="border-b border-primary/30 pb-[2vh]"><strong className="text-primary font-extrabold">FastAPI</strong> for document extraction, matching, courses and demo sessions</p>
        <p className="border-b border-primary/30 pb-[2vh]"><strong className="text-primary font-extrabold">JSON/CSV</strong> data snapshots and a locally generated career-vector index</p>
        <p><strong className="text-primary font-extrabold">OpenAPI</strong> contracts and generated TypeScript clients; no SQL server required</p>
      </div>
    </div>
  );
}
