import { useRouter } from 'next/router';
import { useEffect, useRef } from 'react';

export default function AppDocs() {
    const router = useRouter();
    const iframeRef = useRef<HTMLIFrameElement>(null);
    const path = Array.isArray(router.query.doc) ? router.query.doc.join('/') : router.query.doc;

    // when user clicks on a link in the frame, sync the url bar
    useEffect(() => {
        const handleIframeLoad = () => {
            if (iframeRef?.current?.contentWindow) {
                const iframeLocation = iframeRef.current.contentWindow.location;
                const newUrl = `/appdocs${iframeLocation.pathname.replace('/docs', '')}${iframeLocation.hash}`;
                if (window.location.pathname !== newUrl) {
                    window.history.pushState({}, '', newUrl);
                }
            }
        };

        const iframe = iframeRef.current;
        if (iframe) iframe.addEventListener('load', handleIframeLoad);

        return () => {
            if (iframe) {
                iframe.removeEventListener('load', handleIframeLoad);
            }
        };
    }, []);

    // when a page is first visited, scroll to the hash
    useEffect(() => {
        const scrollToHash = () => {
            const hash = window.location.hash;
            if (hash && iframeRef.current) {
                // Wait for the iframe to load and then scroll to the hash
                iframeRef.current.onload = () => {
                    if (!iframeRef?.current?.contentWindow) return;
                    const element = iframeRef.current.contentWindow.document.getElementById(hash.replace('#',''));
                    if (element) element.scrollIntoView();
                };
            }
        };

        scrollToHash();
    }, [router.asPath]); // Depend on the full path, including hash


    // when a change occurs in the frame, it should send a signal to us here
    // so we can handle that change, but it's not apparent this is actually
    // doing anything at the moment.
    useEffect(() => {
        const handleMessage = (event: MessageEvent) => {
            if (event.origin !== document.location.origin) {
                console.error("Untrusted origin");
                return;
            }

            if (event.data?.url) {
                const iframeURL = new URL(event.data.url);
                const path = iframeURL.pathname;
                const search = iframeURL.search;
                iframeURL.hash = window.location.hash;

                const newUrl = `/appdocs${path.replace('/docs', '')}${search}${window.location.hash}`;
                if (window.location.href !== newUrl) {
                    window.history.pushState({}, '', newUrl);
                }
            }
        };

        window.addEventListener('message', handleMessage);

        return () => {
            window.removeEventListener('message', handleMessage);
        };
    }, []);


    const iframeSrc = `/docs/${path || '/index.html'}`;

    return <iframe ref={iframeRef} src={iframeSrc} style={{ width: '100%', height: '100%' }} />;
}
