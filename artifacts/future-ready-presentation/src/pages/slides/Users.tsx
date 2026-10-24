export default function Users() {
  return (
    <div className="w-screen h-screen overflow-hidden relative bg-bg text-text font-body">
      <h1 className="absolute left-[6vw] top-[8vh] w-[88vw] text-[3.8vw] leading-[1.12] font-display font-extrabold tracking-tight">Who FutureReady is designed for</h1>
      <div className="absolute left-[6vw] right-[6vw] top-[34vh] grid grid-cols-3 gap-[4vw] text-[2.25vw] leading-[1.35]">
        <p className="border-t border-primary pt-[4vh]">Students and recent graduates exploring AI-related careers</p>
        <p className="border-t border-primary pt-[4vh]">Early-career professionals and career changers comparing transferable experience</p>
        <p className="border-t border-primary pt-[4vh]">Career advisers supporting authorized, human-led exploration</p>
      </div>
      <p className="absolute left-0 bottom-[9vh] w-full bg-primary text-bg py-[4vh] px-[6vw] text-[2.3vw] leading-[1.25] font-semibold">English-first interface with an optional Chinese interface</p>
    </div>
  );
}
