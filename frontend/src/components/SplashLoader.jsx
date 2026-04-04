import React, { useEffect, useState } from 'react';
import { Brain } from 'lucide-react';

const SplashLoader = ({ onComplete }) => {
    const [animationState, setAnimationState] = useState('entering');

    useEffect(() => {
        // Timeline for the splash screen
        const timer1 = setTimeout(() => {
            setAnimationState('exiting');
        }, 2200); // Wait 2.2 seconds then start exit animation

        const timer2 = setTimeout(() => {
            if (onComplete) onComplete();
        }, 2700); // 500ms after exit starts, unmount

        return () => {
            clearTimeout(timer1);
            clearTimeout(timer2);
        };
    }, [onComplete]);

    return (
        <div style={{
            position: 'fixed',
            inset: 0,
            zIndex: 9999,
            backgroundColor: '#0a0a0f',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            willChange: 'opacity, transform',
            transition: 'opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1), transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
            opacity: animationState === 'exiting' ? 0 : 1,
            transform: animationState === 'exiting' ? 'scale(1.05)' : 'scale(1)',
            pointerEvents: 'none',
        }}>
            {/* Animated Logo Container */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
            }}>
                <div style={{ position: 'relative' }}>
                    {/* GPU accelerated glow using separate div */}
                    <div style={{
                        position: 'absolute',
                        inset: -10,
                        backgroundColor: '#6366f1',
                        borderRadius: '50%',
                        filter: 'blur(20px)',
                        zIndex: 0,
                        animation: 'pulse-glow-optimized 2s ease-in-out infinite',
                    }} />
                    
                    <div style={{
                        position: 'relative',
                        zIndex: 1,
                        animation: 'slide-in-left 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards',
                        willChange: 'transform, opacity',
                    }}>
                        <Brain size={64} color="#a5b4fc" strokeWidth={1.5} />
                    </div>
                </div>
                
                <div style={{
                    overflow: 'hidden',
                    whiteSpace: 'nowrap',
                    animation: 'reveal-text 1s cubic-bezier(0.2, 0.8, 0.2, 1) forwards',
                    animationDelay: '0.2s',
                    opacity: 0, // Starts hidden before animation
                    willChange: 'clip-path, opacity',
                    clipPath: 'inset(0 100% 0 0)',
                }}>
                    <span style={{ 
                        fontSize: '48px', 
                        fontWeight: 800, 
                        letterSpacing: '-0.02em',
                        color: '#ffffff',
                    }}>
                        NeuroTrade<span style={{ color: '#6366f1' }}>.ai</span>
                    </span>
                </div>
            </div>

            {/* Subtitle / loading indicator */}
            <div style={{
                marginTop: '40px',
                display: 'flex',
                gap: '8px',
                animation: 'fade-in-up 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards',
                animationDelay: '0.8s',
                opacity: 0,
                willChange: 'opacity, transform',
            }}>
                <div className="dot" style={{ animationDelay: '0ms' }}></div>
                <div className="dot" style={{ animationDelay: '150ms' }}></div>
                <div className="dot" style={{ animationDelay: '300ms' }}></div>
            </div>

            <style>{`
                @keyframes pulse-glow-optimized {
                    0%, 100% { opacity: 0.4; transform: scale(0.8); }
                    50% { opacity: 0.8; transform: scale(1.2); }
                }
                @keyframes slide-in-left {
                    from { transform: translateX(-40px); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes reveal-text {
                    from { clip-path: inset(0 100% 0 0); opacity: 0; }
                    to { clip-path: inset(0 0 0 0); opacity: 1; }
                }
                @keyframes fade-in-up {
                    from { opacity: 0; transform: translateY(15px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .dot {
                    width: 8px;
                    height: 8px;
                    background-color: #6366f1;
                    border-radius: 50%;
                    willChange: transform;
                    animation: bounce-dot 1.2s infinite cubic-bezier(0.4, 0, 0.2, 1) both;
                }
                @keyframes bounce-dot {
                    0%, 80%, 100% { transform: scale(0); }
                    40% { transform: scale(1); }
                }
            `}</style>
        </div>
    );
};

export default SplashLoader;
