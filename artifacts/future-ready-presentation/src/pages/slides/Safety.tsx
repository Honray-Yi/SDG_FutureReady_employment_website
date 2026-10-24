export default function Safety() {
  return (
    <div className="w-screen h-screen overflow-hidden relative bg-bg text-text font-body">
      <h1 className="absolute left-[6vw] top-[8vh] w-[88vw] text-[3.8vw] leading-[1.12] font-display font-extrabold tracking-tight">A working demo, with explicit safety boundaries</h1>
      <div className="absolute left-[6vw] top-[32vh] bottom-[10vh] w-[44vw] bg-primary text-bg p-[3vw] flex flex-col justify-between text-[2vw] leading-[1.3]">
        <p>Server-validated shared demo sign-in, session restoration and logout</p>
        <p>PBKDF2-HMAC-SHA256: 600,000 iterations and a random salt</p>
        <p>HttpOnly cookie, two-hour in-memory sessions and login rate limits</p>
      </div>
      <div className="absolute left-[56vw] top-[36vh] right-[6vw] flex flex-col gap-[6vh] text-[2.15vw] leading-[1.3]">
        <p>Resume processing requires consent; files, extracted text and resume vectors are not retained</p>
        <p className="text-accent font-semibold">Public demo identity is not production authentication or private-data authorization</p>
      </div>
    </div>
  );
}
