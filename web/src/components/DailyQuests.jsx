import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import PixelIcon from './PixelIcon';
import './DailyQuests.css';

export default function DailyQuests() {
    const [quests, setQuests] = useState([
        { id: 'track', title: 'Track 1 Opportunity', xp: 10, icon: 'compass', reached: 0, target: 1 },
        { id: 'analyze', title: 'Use Am I Ready?', xp: 15, icon: 'search', reached: 0, target: 1 },
        { id: 'view', title: 'View 3 Articles', xp: 15, icon: 'books', reached: 0, target: 3 },
        { id: 'login', title: 'Login Daily', xp: 10, icon: 'flame', reached: 1, target: 1 },
    ]);

    return (
        <div className="daily-quests-container pixel-box">
            <div className="pixel-banner">
                <PixelIcon name="scroll" size={16} color="#000" />
                <span className="banner-text" style={{ marginLeft: '8px' }}>DAILY QUESTS</span>
            </div>

            <div className="quest-list">
                {quests.map((quest) => {
                    const isDone = quest.reached >= quest.target;
                    const progress = (quest.reached / quest.target) * 100;

                    return (
                        <div key={quest.id} className={`quest-item ${isDone ? 'done' : ''}`}>
                            <div className="quest-header">
                                <PixelIcon
                                    name={quest.icon}
                                    size={20}
                                    color={isDone ? 'var(--pixel-green)' : '#888'}
                                    active={isDone}
                                />
                                <span className="quest-title">{quest.title}</span>
                                <span className="quest-xp">+{quest.xp} XP</span>
                            </div>

                            <div className="quest-progress-bar">
                                <div className="quest-progress-fill" style={{ width: `${progress}%`, backgroundColor: isDone ? 'var(--pixel-green)' : '#555' }} />
                                {isDone && <span className="quest-check"><PixelIcon name="check" size={12} /></span>}
                            </div>
                        </div>
                    );
                })}
            </div>

            <div className="daily-bonus-banner">
                BONUS: Complete All for +50 XP!
            </div>
        </div>
    );
}
