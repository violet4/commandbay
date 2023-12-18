import { useEffect } from 'react';
import { useRouter } from 'next/router';

export default function AppDocsIndex() {
    const router = useRouter();

    useEffect(() => {
        // Redirect to a default documentation page
        router.push('/appdocs/index.html');
    }, [router]);

    return (
        <div>
            <h1>Loading..</h1>
        </div>
    );
}
