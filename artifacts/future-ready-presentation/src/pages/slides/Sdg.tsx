export default function Sdg() {
  return (
    <div className="w-screen h-screen overflow-hidden relative bg-bg text-text font-body">
      <h1 className="absolute left-[6vw] top-[8vh] w-[88vw] text-[3.8vw] leading-[1.12] font-display font-extrabold tracking-tight">SDG alignment: learning, work and inclusion</h1>
      <div className="absolute left-[6vw] top-[31vh] w-[48vw] flex flex-col gap-[5vh] text-[2.2vw] leading-[1.3]">
        <p><strong className="text-primary font-extrabold">SDG 4.4:</strong> access to learning resources for job-relevant skills</p>
        <p><strong className="text-primary font-extrabold">SDG 8.5:</strong> support informed career preparation—not guaranteed employment</p>
        <p><strong className="text-primary font-extrabold">SDG 10.2:</strong> bilingual access and clearly stated learning costs</p>
      </div>
      <div className="absolute right-[6vw] top-[31vh] bottom-[10vh] w-[34vw] bg-primary text-bg p-[3vw] flex flex-col justify-between text-[2vw] leading-[1.3]">
        <p>All 65 roles also carry application-specific SDG goals, targets and source links</p>
        <p className="font-semibold">Potential alignment is not UN endorsement or measured social impact</p>
      </div>
    </div>
  );
}
