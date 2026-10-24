export default function Delivery() {
  return (
    <div className="w-screen h-screen overflow-hidden relative bg-primary text-bg font-body">
      <h1 className="absolute left-[6vw] top-[8vh] w-[88vw] text-[3.8vw] leading-[1.12] font-display font-extrabold tracking-tight">Verified delivery—and responsible use</h1>
      <p className="absolute left-[6vw] top-[26vh] text-[2.4vw] leading-[1.1]"><strong className="text-[8vw] font-extrabold">65</strong> backend regression tests passed</p>
      <div className="absolute left-[6vw] right-[6vw] top-[47vh] grid grid-cols-2 gap-x-[6vw] gap-y-[5vh] text-[2vw] leading-[1.28]">
        <p>Independent source-package installation, fresh model download and index creation passed</p>
        <p>Interface regeneration, TypeScript checks, production build and full HTTP workflow passed</p>
        <p>GitHub-ready source includes data, frontend, backend, interface definitions and setup instructions</p>
        <p>First setup needs internet; inference runs on the application backend, not in the browser</p>
      </div>
    </div>
  );
}
