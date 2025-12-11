/**
 * APOLLO CyberSentinel - Enhanced Effects Library
 * Adds legendary animations to any page
 * Version: 2.0
 */

(function() {
    'use strict';

    // Initialize all effects
    function initApolloEffects() {
        addNeuralCanvas();
        addParticleSystem();
        addFloatingOrbs();
        addGridOverlay();
        addScanLine();
        enhanceInteractions();
    }

    // Neural Network Canvas
    function addNeuralCanvas() {
        // Check if canvas already exists
        if (document.getElementById('apollo-neural-canvas')) return;

        const canvas = document.createElement('canvas');
        canvas.id = 'apollo-neural-canvas';
        canvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            opacity: 0.5;
            pointer-events: none;
        `;
        document.body.insertBefore(canvas, document.body.firstChild);

        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        class NeuralNode {
            constructor() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.z = Math.random() * 1000;
                this.vx = (Math.random() - 0.5) * 0.8;
                this.vy = (Math.random() - 0.5) * 0.8;
                this.vz = (Math.random() - 0.5) * 0.8;
                this.size = Math.random() * 3 + 1;
                this.hue = Math.random() * 60 + 180;
                this.pulsePhase = Math.random() * Math.PI * 2;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;
                this.z += this.vz;
                this.pulsePhase += 0.05;

                if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
                if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
                if (this.z < 0 || this.z > 1000) this.vz *= -1;
            }

            draw() {
                const scale = 1000 / (1000 + this.z);
                const x = this.x * scale + (canvas.width * (1 - scale)) / 2;
                const y = this.y * scale + (canvas.height * (1 - scale)) / 2;
                const size = this.size * scale * (1 + Math.sin(this.pulsePhase) * 0.3);
                const alpha = 0.4 * scale * (1 + Math.sin(this.pulsePhase) * 0.2);

                const gradient = ctx.createRadialGradient(x, y, 0, x, y, size * 3);
                gradient.addColorStop(0, `hsla(${this.hue}, 100%, 60%, ${alpha})`);
                gradient.addColorStop(1, `hsla(${this.hue}, 100%, 60%, 0)`);
                
                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(x, y, size * 3, 0, Math.PI * 2);
                ctx.fill();

                ctx.fillStyle = `hsla(${this.hue}, 100%, 70%, ${alpha * 1.5})`;
                ctx.beginPath();
                ctx.arc(x, y, size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        const nodes = [];
        for (let i = 0; i < 120; i++) {
            nodes.push(new NeuralNode());
        }

        function animate() {
            ctx.fillStyle = 'rgba(10, 0, 20, 0.08)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            nodes.forEach(node => {
                node.update();
                node.draw();
            });

            for (let i = 0; i < nodes.length; i++) {
                for (let j = i + 1; j < nodes.length; j++) {
                    const dx = nodes[i].x - nodes[j].x;
                    const dy = nodes[i].y - nodes[j].y;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < 180) {
                        const alpha = 0.15 * (1 - distance / 180);
                        const gradient = ctx.createLinearGradient(
                            nodes[i].x, nodes[i].y,
                            nodes[j].x, nodes[j].y
                        );
                        gradient.addColorStop(0, `rgba(0, 245, 255, ${alpha})`);
                        gradient.addColorStop(0.5, `rgba(189, 0, 255, ${alpha * 0.8})`);
                        gradient.addColorStop(1, `rgba(0, 255, 136, ${alpha})`);
                        
                        ctx.strokeStyle = gradient;
                        ctx.lineWidth = 1.5;
                        ctx.beginPath();
                        ctx.moveTo(nodes[i].x, nodes[i].y);
                        ctx.lineTo(nodes[j].x, nodes[j].y);
                        ctx.stroke();
                    }
                }
            }

            requestAnimationFrame(animate);
        }

        animate();

        window.addEventListener('resize', () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        });
    }

    // Particle System
    function addParticleSystem() {
        if (document.getElementById('apollo-particles')) return;

        const container = document.createElement('div');
        container.id = 'apollo-particles';
        container.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
            pointer-events: none;
        `;
        document.body.insertBefore(container, document.body.firstChild);

        const particleTypes = [
            { size: '3px', color: '#00f5ff', shadow: '0 0 10px #00f5ff' },
            { size: '2px', color: '#bd00ff', shadow: '0 0 8px #bd00ff' },
            { size: '4px', color: '#00ff88', shadow: '0 0 12px #00ff88' }
        ];

        for (let i = 0; i < 80; i++) {
            setTimeout(() => {
                const particle = document.createElement('div');
                const type = particleTypes[Math.floor(Math.random() * 3)];
                
                particle.style.cssText = `
                    position: absolute;
                    width: ${type.size};
                    height: ${type.size};
                    background: ${type.color};
                    box-shadow: ${type.shadow};
                    border-radius: 50%;
                    left: ${Math.random() * 100}%;
                    animation: apolloParticleFloat ${Math.random() * 8 + 6}s linear infinite;
                    animation-delay: ${Math.random() * 5}s;
                    opacity: 0;
                `;
                
                container.appendChild(particle);
            }, i * 80);
        }

        // Add animation if not exists
        if (!document.getElementById('apollo-particle-animation')) {
            const style = document.createElement('style');
            style.id = 'apollo-particle-animation';
            style.textContent = `
                @keyframes apolloParticleFloat {
                    0% {
                        opacity: 0;
                        transform: translateY(100vh) scale(0) rotate(0deg);
                    }
                    10% { opacity: 1; }
                    90% { opacity: 1; }
                    100% {
                        opacity: 0;
                        transform: translateY(-100px) scale(1.5) rotate(360deg);
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Floating Orbs
    function addFloatingOrbs() {
        if (document.getElementById('apollo-orbs')) return;

        const orbs = [
            { size: '300px', color: '#00f5ff', top: '10%', left: '10%', delay: '0s' },
            { size: '400px', color: '#bd00ff', top: '60%', right: '10%', delay: '5s' },
            { size: '250px', color: '#00ff88', bottom: '20%', left: '30%', delay: '10s' }
        ];

        orbs.forEach((orb, index) => {
            const element = document.createElement('div');
            element.id = `apollo-orb-${index}`;
            element.style.cssText = `
                position: fixed;
                width: ${orb.size};
                height: ${orb.size};
                background: ${orb.color};
                border-radius: 50%;
                filter: blur(60px);
                opacity: 0.3;
                animation: apolloOrbFloat 20s ease-in-out infinite;
                animation-delay: ${orb.delay};
                pointer-events: none;
                z-index: 0;
                ${orb.top ? 'top: ' + orb.top : ''};
                ${orb.bottom ? 'bottom: ' + orb.bottom : ''};
                ${orb.left ? 'left: ' + orb.left : ''};
                ${orb.right ? 'right: ' + orb.right : ''};
            `;
            document.body.insertBefore(element, document.body.firstChild);
        });

        if (!document.getElementById('apollo-orb-animation')) {
            const style = document.createElement('style');
            style.id = 'apollo-orb-animation';
            style.textContent = `
                @keyframes apolloOrbFloat {
                    0%, 100% { transform: translate(0, 0) scale(1); }
                    25% { transform: translate(50px, -50px) scale(1.1); }
                    50% { transform: translate(-30px, 30px) scale(0.9); }
                    75% { transform: translate(30px, 50px) scale(1.05); }
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Grid Overlay
    function addGridOverlay() {
        if (document.getElementById('apollo-grid')) return;

        const grid = document.createElement('div');
        grid.id = 'apollo-grid';
        grid.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(rgba(0, 245, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 245, 255, 0.03) 1px, transparent 1px);
            background-size: 50px 50px;
            z-index: 0;
            opacity: 0.3;
            animation: apolloGridMove 20s linear infinite;
            pointer-events: none;
        `;
        document.body.insertBefore(grid, document.body.firstChild);

        if (!document.getElementById('apollo-grid-animation')) {
            const style = document.createElement('style');
            style.id = 'apollo-grid-animation';
            style.textContent = `
                @keyframes apolloGridMove {
                    0% { transform: translate(0, 0); }
                    100% { transform: translate(50px, 50px); }
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Scan Line
    function addScanLine() {
        if (document.getElementById('apollo-scan')) return;

        const scan = document.createElement('div');
        scan.id = 'apollo-scan';
        scan.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, transparent, #00f5ff, #00f5ff, transparent);
            animation: apolloScanLine 4s linear infinite;
            z-index: 100;
            opacity: 0.6;
            box-shadow: 0 0 20px #00f5ff;
            pointer-events: none;
        `;
        document.body.appendChild(scan);

        if (!document.getElementById('apollo-scan-animation')) {
            const style = document.createElement('style');
            style.id = 'apollo-scan-animation';
            style.textContent = `
                @keyframes apolloScanLine {
                    0% { transform: translateY(0); }
                    100% { transform: translateY(100vh); }
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Enhanced Interactions
    function enhanceInteractions() {
        // Add 3D tilt to cards on mouse move
        document.querySelectorAll('.card, .feature-card, .stat-box').forEach(card => {
            card.addEventListener('mousemove', function(e) {
                const rect = this.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                const rotateX = (y - centerY) / 20;
                const rotateY = (centerX - x) / 20;
                
                this.style.transform = `translateY(-10px) scale(1.03) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
            });

            card.addEventListener('mouseleave', function() {
                this.style.transform = '';
            });
        });

        // Add ripple effect to buttons
        document.querySelectorAll('button, .btn, .cta-button').forEach(button => {
            button.addEventListener('click', function(e) {
                const ripple = document.createElement('div');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;

                ripple.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    background: rgba(255, 255, 255, 0.5);
                    border-radius: 50%;
                    transform: scale(0);
                    animation: apolloRipple 0.6s ease-out;
                    left: ${x}px;
                    top: ${y}px;
                    pointer-events: none;
                `;

                this.style.position = 'relative';
                this.style.overflow = 'hidden';
                this.appendChild(ripple);

                setTimeout(() => ripple.remove(), 600);
            });
        });

        if (!document.getElementById('apollo-ripple-animation')) {
            const style = document.createElement('style');
            style.id = 'apollo-ripple-animation';
            style.textContent = `
                @keyframes apolloRipple {
                    to {
                        transform: scale(2);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initApolloEffects);
    } else {
        initApolloEffects();
    }

    // Expose global function for manual initialization
    window.initApolloEffects = initApolloEffects;

})();
