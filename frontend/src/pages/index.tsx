import Image from 'next/image'

const Gt = () => {
  return (
    <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
      -&gt;
    </span>
  );
};

export default function Index() {
  return (
    <main>
      <h1 className="text-3xl">CommandBay</h1>
      <div>
        Welcome to CommandBay!
      </div>
    </main>
  )
}
