import { useCallback } from 'react';

// Define the types for the onSave and onCancel callbacks
type UseSaveCancelKeysProps = {
    onEnter: () => void;
    onEscape: () => void;
};

export function useSaveCancelKeys({ onEnter: positiveAction, onEscape: negativeAction }: UseSaveCancelKeysProps) {
    const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            positiveAction();
        } else if (e.key === 'Escape') {
            negativeAction();
        }
    }, [positiveAction, negativeAction]);

    return { onKeyDown: handleKeyDown };
}

type KeyEvents = {
    Escape?: () => void;
    Enter?: () => void;
};

export const useKeyPressHandlers = (keyEvents: KeyEvents) => {
    const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
        const fn = keyEvents[e.key as keyof KeyEvents];
        if (fn !== undefined)
            fn();
    }, [keyEvents]);
    return {onKeyDown: handleKeyDown};
};

export const json_headers = {'Content-Type': 'application/json'};

export const requestConfirmation = (callback: () => void) => {
    return () => {
        if (window.confirm("Are you sure you want to proceed?"))
            callback();
    };
};
