export default function Sources() {
  return (
    <div className="w-screen h-screen overflow-hidden relative bg-bg text-text font-body">
      <h1 className="absolute left-[6vw] top-[8vh] w-[88vw] text-[3.8vw] leading-[1.12] font-display font-extrabold tracking-tight">Sources and learning recommendations</h1>
      <div className="absolute left-[6vw] top-[31vh] w-[45vw] flex flex-col gap-[4vh] text-[2vw] leading-[1.3]">
        <p>The project-owner-supplied CSV is the 65-role matching catalogue</p>
        <p>Courses link to official providers with reasons, cost conditions and review dates</p>
        <p>UN goal pages support curated role-level SDG explanations</p>
      </div>
      <div className="absolute left-[58vw] top-[31vh] right-[6vw] border-t border-primary pt-[4vh] flex flex-col gap-[6vh] text-[2.1vw] leading-[1.3] text-accent">
        <p>O*NET, BLS, arXiv and Malaysian sources remain separate historical reference data</p>
        <p>Provenance and redistribution caveats are recorded in README</p>
      </div>
    </div>
  );
}
