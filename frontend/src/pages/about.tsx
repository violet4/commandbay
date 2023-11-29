import Image from 'next/image'

const Gt = () => {
  return (
    <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
      -&gt;
    </span>
  );
};

export default function About() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      About me! Yay!
    </main>
  )
}
