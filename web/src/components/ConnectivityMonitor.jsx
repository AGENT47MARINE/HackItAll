import React, { useState, useEffect } from 'react';

export const useConnectivity = () => {
    const [connectionState, setConnectionState] = useState({
        effectiveType: 'unknown',
        saveData: false,
        isPoor: false
    });

    useEffect(() => {
        const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;

        const updateConnectionStatus = () => {
            if (connection) {
                const isPoor = ['slow-2g', '2g', '3g'].includes(connection.effectiveType) || connection.saveData;
                setConnectionState({
                    effectiveType: connection.effectiveType,
                    saveData: connection.saveData,
                    isPoor: isPoor
                });
            }
        };

        if (connection) {
            connection.addEventListener('change', updateConnectionStatus);
            updateConnectionStatus();
        }

        return () => {
            if (connection) {
                connection.removeEventListener('change', updateConnectionStatus);
            }
        };
    }, []);

    return connectionState;
};

export const ConnectivityMonitor = ({ children }) => {
    const { isPoor, effectiveType } = useConnectivity();
    const [dismissed, setDismissed] = useState(false);
    const [liteMode, setLiteMode] = useState(localStorage.getItem('liteMode') === 'true');

    useEffect(() => {
        if (isPoor && !liteMode && !dismissed) {
            // Auto-trigger lite mode suggestion could go here
        }
    }, [isPoor, liteMode, dismissed]);

    const toggleLiteMode = () => {
        const newState = !liteMode;
        setLiteMode(newState);
        localStorage.setItem('liteMode', newState);
        window.location.reload(); // Reload to force lite-assets from server
    };

    return (
        <div className={liteMode ? 'lite-mode-active' : ''}>
            {isPoor && !liteMode && !dismissed && (
                <div className="fixed bottom-4 left-4 right-4 z-[9999] animate-in">
                    <div className="bg-amber-500/90 backdrop-blur text-white px-6 py-4 rounded-2xl flex items-center justify-between shadow-2xl border border-white/20">
                        <div className="flex items-center gap-3">
                            <span className="text-2xl">📶</span>
                            <div>
                                <p className="font-bold text-sm">Poor Connection Detected ({effectiveType})</p>
                                <p className="text-xs opacity-90">Switch to Lite Mode for a faster, text-only experience.</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={toggleLiteMode}
                                className="bg-white text-amber-600 px-4 py-1.5 rounded-lg text-xs font-bold hover:bg-white/90 transition-colors uppercase"
                            >
                                Switch to Lite
                            </button>
                            <button
                                onClick={() => setDismissed(true)}
                                className="text-white/60 hover:text-white"
                            >
                                ✕
                            </button>
                        </div>
                    </div>
                </div>
            )}
            {children}
        </div>
    );
};
