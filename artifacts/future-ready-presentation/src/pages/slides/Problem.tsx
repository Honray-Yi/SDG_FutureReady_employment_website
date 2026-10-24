export default function Problem() {
  return (
    <div className="w-screen h-screen overflow-hidden relative bg-bg text-text font-body">
      <h1 className="absolute left-[6vw] top-[22vh] w-[36vw] text-[4.5vw] leading-[1.13] font-display font-extrabold tracking-tight">The problem: career exploration is fragmented</h1>
      <div className="absolute right-0 top-0 bottom-0 w-[52vw] bg-primary text-bg px-[4vw] flex flex-col justify-center gap-[5vh] text-[2vw] leading-[1.3]">
        <p>Students and career changers struggle to connect experience with technical role descriptions</p>
        <p>Learning resources are scattered across providers</p>
        <p>Unexplained scores and unclear course costs can mislead decisions</p>
        <p className="font-extrabold">Users need one transparent starting point—not an automated hiring verdict</p>
      </div>
    </div>
  );
}
