import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import PremiumIcon from './PremiumIcon';
import './VoiceAssistant.css';

const VoiceAssistant = () => {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const transcriptRef = useRef('');
    const [isProcessing, setIsProcessing] = useState(false);
    const [isError, setIsError] = useState(false);
    const isErrorRef = useRef(false); // Ref for reliable sync check in events
    const isListeningRef = useRef(false); // Ref for watchdog to see current state from closure
    const recognitionRef = useRef(null);
    const retryCountRef = useRef(0);
    const navigate = useNavigate();
    const location = useLocation();

    // Sync refs with state
    useEffect(() => {
        transcriptRef.current = transcript;
    }, [transcript]);

    useEffect(() => {
        isErrorRef.current = isError;
    }, [isError]);

    useEffect(() => {
        isListeningRef.current = isListening;
    }, [isListening]);

    const startRecognition = useCallback(() => {
        if (!window.navigator.onLine) {
            console.warn('VoiceAssistant: Browser is offline. Speech (cloud) will fail.');
            setTranscript('Network unreachable.');
            setIsError(true);
            isErrorRef.current = true;
            return;
        }

        if (recognitionRef.current) {
            try {
                recognitionRef.current.start();
            } catch (e) {
                console.warn('Recognition already started or failed to start:', e);
            }
        }
    }, []);

    const handleVoiceAction = useCallback(async (manualTranscript = null) => {
        const textToProcess = manualTranscript || transcriptRef.current;
        if (!textToProcess || textToProcess === 'Listening...') return;

        setIsProcessing(true);
        const command = textToProcess.toLowerCase().trim();
        console.log('Voice Command:', command);

        // 1. Navigation Mapping
        const pageTargets = {
            'discover': '/discover',
            'tracked': '/tracked',
            'saved': '/tracked',
            'profile': '/profile',
            'leagues': '/leagues',
            'home': '/',
            'dashboard': '/tracked',
            'opportunities': '/opportunities',
            'onboarding': '/onboarding',
            'match': '/discover',
            'for you': '/discover',
            'recommendations': '/discover'
        };

        // Check for navigation commands
        for (const [key, path] of Object.entries(pageTargets)) {
            if (command.includes(key) && (command.includes('open') || command.includes('go to') || command.includes('show') || command.includes('find'))) {
                navigate(path);
                setTranscript(`Navigating to ${key}...`);
                setIsError(false);
                setTimeout(() => setTranscript(''), 2000);
                setIsProcessing(false);
                return;
            }
        }

        // 2. Item Specific Navigation (e.g., "open [hackathon name]")
        if (command.includes('open') || command.includes('show') || command.includes('view') || command.includes('detail')) {
            // Find the name mentioned. Usually "open [Name]"
            let targetName = command.replace(/(open|show|view|detail|me|the|go to)/g, '').trim();

            if (targetName.length > 2) {
                // Try to find matching elements on current page first (for speed)
                const cards = document.querySelectorAll('.card-title, .opportunity-title');
                let matchedId = null;

                for (const card of cards) {
                    if (card.textContent.toLowerCase().includes(targetName)) {
                        // Found a match on page. Now find the closest link or action.
                        const cardParent = card.closest('.tracked-glass-card') || card.closest('.opportunity-card');
                        if (cardParent) {
                            // Usually we can extract ID or just find the visit/detail button
                            const visitBtn = cardParent.querySelector('a') || cardParent.querySelector('.card-action-btn');
                            if (visitBtn) {
                                visitBtn.click();
                                setTranscript(`Opening ${card.textContent}...`);
                                setTimeout(() => setTranscript(''), 2000);
                                setIsProcessing(false);
                                return;
                            }
                        }
                    }
                }
            }
        }

        // 3. Scroll Commands
        if (command.includes('scroll down')) {
            window.scrollBy({ top: 500, behavior: 'smooth' });
        } else if (command.includes('scroll up')) {
            window.scrollBy({ top: -500, behavior: 'smooth' });
        } else if (command.includes('scroll to top')) {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } else if (command.includes('scroll to bottom')) {
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
        }

        // Fallback or No Match
        console.log('No specific action matched for:', command);
        setTimeout(() => {
            setTranscript('');
            setIsProcessing(false);
        }, 2000);
    }, [navigate]);

    const toggleListening = async () => {
        if (isListening) {
            recognitionRef.current?.stop();
            setIsListening(false);
            isListeningRef.current = false;
        } else {
            setTranscript('');
            setIsError(false);
            isErrorRef.current = false;
            retryCountRef.current = 0;
            startRecognition();
        }
    };

    // Initialize Speech Recognition once
    useEffect(() => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition || recognitionRef.current) return;

        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        let watchdog;

        recognition.onstart = () => {
            setIsListening(true);
            isListeningRef.current = true;
            setTranscript('Listening...');
            transcriptRef.current = 'Listening...';
            // We don't reset retryCount here, we reset it in toggleListening (user start)
            console.log('Voice recognition session started.');

            if (watchdog) clearTimeout(watchdog);
            watchdog = setTimeout(() => {
                if (isListeningRef.current && transcriptRef.current === 'Listening...') {
                    console.warn('Speech recognition hung, stopping...');
                    recognition.stop();
                }
            }, 8000);
        };

        recognition.onresult = (event) => {
            if (watchdog) clearTimeout(watchdog);
            const current = event.resultIndex;
            const result = event.results[current][0].transcript;
            setTranscript(result);
            transcriptRef.current = result;
        };

        recognition.onend = () => {
            if (watchdog) clearTimeout(watchdog);
            setIsListening(false);
            isListeningRef.current = false;
            const finalTranscript = transcriptRef.current;

            // Use refs to check if we should process
            if (!isErrorRef.current && finalTranscript && finalTranscript !== 'Listening...') {
                handleVoiceAction(finalTranscript);
            }
        };

        recognition.onerror = (event) => {
            if (watchdog) clearTimeout(watchdog);
            console.error('Speech recognition error:', event.error);

            // SPECIAL CASE: 'network' error usually means browser-side service issue
            if (event.error === 'network' && retryCountRef.current < 2) {
                // Don't kill everything yet, try one soft restart with cooldown
                retryCountRef.current += 1;
                console.log(`Speech Engine: Networking issue. Soft restart #${retryCountRef.current} in 3s...`);

                // Keep the UI in a "reconnecting" state
                setTranscript('Engine reconnecting...');

                setTimeout(() => {
                    // Check if we didn't stop in the meantime
                    if (recognitionRef.current && !isListeningRef.current) {
                        try {
                            recognitionRef.current.start();
                        } catch (e) {
                            console.error('Failed to restart recognition:', e);
                        }
                    }
                }, 3000); // 3s cooldown is better than 1s to avoid spamming the OS engine
                return;
            }

            setIsListening(false);
            isListeningRef.current = false;
            setIsError(true);
            isErrorRef.current = true;

            let errorMessage = 'Error occurred';
            if (event.error === 'network') {
                errorMessage = 'Voice service unreachable. Check connection.';
            } else if (event.error === 'not-allowed') {
                errorMessage = 'Microphone access denied.';
            } else if (event.error === 'no-speech') {
                setIsError(false);
                isErrorRef.current = false;
                setTranscript('');
                return;
            }

            setTranscript(errorMessage);
            setTimeout(() => {
                if (!isListeningRef.current) {
                    setTranscript('');
                    setIsError(false);
                    isErrorRef.current = false;
                }
            }, 5000);
        };

        recognitionRef.current = recognition;

        return () => {
            if (watchdog) clearTimeout(watchdog);
            try { recognition.stop(); } catch (e) { }
        };
    }, [handleVoiceAction]); // Only depends on the action handler

    return (
        <div className="voice-assistant-container">
            <AnimatePresence>
                {(isListening || transcript) && (
                    <motion.div
                        className={`voice-transcript-bubble ${isError ? 'error-bubble' : ''} ${isProcessing ? 'processing-bubble' : ''}`}
                        initial={{ opacity: 0, scale: 0.8, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.8, y: 20 }}
                    >
                        <div className="transcript-content">
                            {isListening && <div className="listening-pulse" />}
                            {isError && <PremiumIcon name="shield" size={14} color="#ff3b30" />}
                            <p>{transcript}</p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            <motion.button
                className={`voice-fab ${isListening ? 'listening' : ''} ${isProcessing ? 'processing' : ''}`}
                onClick={toggleListening}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
            >
                <div className="fab-glow" />
                <PremiumIcon name={isListening ? "mic" : "mic"} size={24} color="#fff" />
                {isListening && (
                    <div className="waves">
                        <span /><span /><span />
                    </div>
                )}
            </motion.button>
        </div>
    );
};

export default VoiceAssistant;
