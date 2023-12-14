import useSWR from 'swr';

export default function About() {
  const {data: version, error} = useSWR('/api/version', (url: string) => fetch(url).then(res => res.json()));

  if (error) return <div>Failed to load rewards</div>;
  const version_text = version?version.version:'Loading..';
  const final_version_text = error?`Failed to load: ${error}`:version_text;
  return (
    <main>
      <h1 className="text-3xl">CommandBay</h1>
      <div>
        Version: {final_version_text}
      </div>
    </main>
  );
}
