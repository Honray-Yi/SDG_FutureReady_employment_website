export default function Scope() {
  return (
    <div className="w-screen h-screen overflow-hidden relative bg-bg text-text font-body">
      <h1 className="absolute left-[6vw] top-[8vh] w-[88vw] text-[3.8vw] leading-[1.12] font-display font-extrabold tracking-tight">Scope: one connected exploration journey</h1>
      <div className="absolute left-[6vw] right-[6vw] top-[30vh] grid grid-cols-2 gap-x-[6vw] gap-y-[5vh] text-[2vw] leading-[1.28]">
        <div className="flex gap-[2vw]"><span className="text-primary text-[4vw] leading-none font-extrabold">01</span><p>Upload a text-based PDF or DOCX, or paste experience text</p></div>
        <div className="flex gap-[2vw]"><span className="text-primary text-[4vw] leading-none font-extrabold">02</span><p>Review and edit the extracted text; inspect keyword evidence</p></div>
        <div className="flex gap-[2vw]"><span className="text-primary text-[4vw] leading-none font-extrabold">03</span><p>Compare the same input with all 65 role descriptions</p></div>
        <div className="flex gap-[2vw]"><span className="text-primary text-[4vw] leading-none font-extrabold">04</span><p>Select a career, read its SDG rationale and explore linked learning resources</p></div>
      </div>
      <p className="absolute left-[6vw] right-[6vw] bottom-[10vh] border-t border-primary pt-[3vh] text-[2vw] leading-[1.3] text-accent">OCR, real-user accounts and hiring decisions are outside this demo</p>
    </div>
  );
}
