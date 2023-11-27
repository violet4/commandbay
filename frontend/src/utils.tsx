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
