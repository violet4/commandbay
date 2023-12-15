import useSWR from 'swr';

const GITHUB_ISSUE_TITLE = encodeURIComponent("SHORT DESCRIPTIVE TITLE");

export default function About() {
  const {data: version, error} = useSWR('/api/version', (url: string) => fetch(url).then(res => res.json()));

  if (error) return <div>Failed to load rewards</div>;
  const version_text = version?version.version:'Loading..';
  const final_version_text = error?`Failed to load: ${error}`:version_text;
  const GITHUB_ISSUE_BODY = encodeURIComponent(`Version ${final_version_text}\nNew Line:`);
  return (
    <main className="pl-5">
      <h1 className="text-3xl">CommandBay</h1>
      <div>
        Version: {final_version_text}
      </div>
      <ul>
        <li>
          <a className="link-style" href="https://github.com/violet4/commandbay">GitHub</a>
          <ul className='pl-5'>
            <li>
              <a className="link-style" href="https://github.com/violet4/commandbay/blob/main/README.md">README.md</a>
            </li>
            <li>
              <a className="link-style" href="https://github.com/violet4/commandbay/issues">Issues</a>
            </li>
            <li>
              <a className="link-style" target="_blank" href={`https://github.com/violet4/commandbay/issues/new?title=${GITHUB_ISSUE_TITLE}&body=${GITHUB_ISSUE_BODY}`}>Submit a new issue</a>
            </li>
          </ul>
        </li>
      </ul>
    </main>
  );
}
