document.addEventListener('DOMContentLoaded', (event) => {
    sendURLToParent();

    // Optional: Listen to hash changes
    window.addEventListener('hashchange', () => {
        sendURLToParent();
    });
});

function sendURLToParent() {
    if (window.parent) {
        window.parent.postMessage({
            url: window.location.href
        }, '*');
    }
}
