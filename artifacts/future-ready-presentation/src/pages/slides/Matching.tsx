export default function Matching() {
  return (
    <div className="w-screen h-screen overflow-hidden relative bg-bg text-text font-body">
      <h1 className="absolute left-[6vw] top-[8vh] text-[3.8vw] leading-[1.12] font-display font-extrabold tracking-tight">How the matching works</h1>
      <div className="absolute left-[6vw] top-[30vh] w-[36vw]">
        <p className="text-[2vw] leading-[1.3] text-muted">Local CPU inference with multilingual-e5-small</p>
        <p className="mt-[4vh] text-[2vw] leading-[1.3]">Native <strong className="block text-[12vw] leading-[1.1] text-primary font-extrabold">384</strong>-dimensional embeddings and cosine similarity</p>
      </div>
      <div className="absolute left-[49vw] top-[30vh] right-[6vw] flex flex-col gap-[5vh] text-[2vw] leading-[1.3]">
        <p>Percentage = max(0, cosine) × 100; scores do not need to sum to 100%</p>
        <p>English or Chinese keyword recognition explains overlap without changing scores</p>
        <p className="text-accent font-semibold">Match percentage is not hiring probability or skill mastery</p>
      </div>
    </div>
  );
}
