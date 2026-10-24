const base = import.meta.env.BASE_URL;

export default function Cover() {
  return (
    <div className="w-screen h-screen overflow-hidden relative bg-bg text-text font-body">
      <div className="absolute right-[2vw] top-[18vh] w-[44vw] h-[60vh] overflow-hidden">
        <img src={`${base}images/website-welcome.jpg`} crossOrigin="anonymous" alt="The orb on the current FutureReady welcome page" className="absolute max-w-none w-[103.7vw] left-[-6.5vw] top-[-19.2vh]" />
      </div>
      <div className="absolute left-[6vw] top-[18vh] w-[49vw]">
        <h1 className="font-display font-extrabold text-[6.5vw] leading-[1.05] tracking-tight">FutureReady</h1>
        <p className="mt-[5vh] text-[2.4vw] leading-[1.3] max-w-[45vw] text-accent">From resume experience to career direction and credible learning resources.</p>
        <p className="mt-[9vh] text-[2vw] leading-[1.3]">Local multilingual semantic matching</p>
        <p className="mt-[3vh] text-[2vw] leading-[1.3] max-w-[44vw] text-muted">65 career descriptions, potential SDG contributions and source-reviewed courses</p>
      </div>
    </div>
  );
}
