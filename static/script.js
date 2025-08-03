// Welcome page glitch animation
document.addEventListener('DOMContentLoaded', function() {
    // Add glitch effect to title
    const title = document.querySelector('.glitch-title');
    if (title) {
        setInterval(() => {
            title.style.textShadow = `
                ${Math.random() * 2 - 1}px ${Math.random() * 2 - 1}px 0 #ff006e,
                ${Math.random() * 2 - 1}px ${Math.random() * 2 - 1}px 0 #8338ec,
                ${Math.random() * 2 - 1}px ${Math.random() * 2 - 1}px 0 #3a86ff
            `;
        }, 100);
    }

    // Chat auto-scroll functionality
    const chatMessages = document.querySelector('.chat-messages');
    if (chatMessages) {
        // Auto-scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Enhanced auto-scroll for option button clicks
        const optionBtns = document.querySelectorAll('.option-btn');
        optionBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                // Add loading indicator
                this.style.opacity = '0.6';
                this.textContent = 'Loading...';
                
                // Scroll after a brief delay to show the loading state
                setTimeout(() => {
                    chatMessages.scrollTo({
                        top: chatMessages.scrollHeight,
                        behavior: 'smooth'
                    });
                }, 200);
            });
        });
        
        // Smooth scroll animation for new messages
        const observer = new MutationObserver(() => {
            setTimeout(() => {
                chatMessages.scrollTo({
                    top: chatMessages.scrollHeight,
                    behavior: 'smooth'
                });
            }, 100);
        });
        
        observer.observe(chatMessages, {
            childList: true,
            subtree: true
        });
    }

    // Mood graph functionality
    const filterBtns = document.querySelectorAll('.filter-btn');
    const chartCanvas = document.getElementById('moodChart');
    
    if (chartCanvas && typeof Chart !== 'undefined') {
        let moodChart;
        
        // Initialize chart
        const ctx = chartCanvas.getContext('2d');
        
        function createChart(data, label) {
            if (moodChart) {
                moodChart.destroy();
            }
            
            const labels = Object.keys(data);
            const values = Object.values(data);
            
            moodChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: `${label} Mood Distribution`,
                        data: values,
                        backgroundColor: 'rgba(139, 92, 246, 0.8)',
                        borderColor: 'rgba(139, 92, 246, 1)',
                        borderWidth: 1,
                        borderRadius: 6,
                        borderSkipped: false,
                        maxBarThickness: 60
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(30, 30, 50, 0.95)',
                            titleColor: '#e0e0e0',
                            bodyColor: '#e0e0e0',
                            borderColor: 'rgba(139, 92, 246, 0.5)',
                            borderWidth: 1,
                            cornerRadius: 8
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: Math.max(...values) + 1,
                            ticks: {
                                stepSize: 1,
                                color: '#a0a0a0',
                                font: {
                                    size: 12
                                }
                            },
                            grid: {
                                color: 'rgba(139, 92, 246, 0.1)'
                            }
                        },
                        x: {
                            ticks: {
                                color: '#a0a0a0',
                                maxRotation: 0,
                                font: {
                                    size: 11
                                }
                            },
                            grid: {
                                display: false
                            }
                        }
                    },
                    animation: {
                        duration: 1000,
                        easing: 'easeInOutQuart'
                    }
                }
            });
        }
        
        // Load mood data and create initial chart
        fetch('/mood-data')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error loading mood data:', data.error);
                    return;
                }
                
                // Set up filter button event listeners
                filterBtns.forEach(btn => {
                    btn.addEventListener('click', () => {
                        // Remove active class from all buttons
                        filterBtns.forEach(b => b.classList.remove('active'));
                        // Add active class to clicked button
                        btn.classList.add('active');
                        
                        // Get filter type and update chart
                        const filter = btn.getAttribute('data-filter');
                        const chartData = data[filter] || {};
                        let label = '';
                        
                        if (filter === 'weekly') {
                            label = 'Past 7 Days';
                        } else if (filter === 'monthly') {
                            label = 'Past Month';
                        } else {
                            label = 'Past Year';
                        }
                        
                        createChart(chartData, label);
                    });
                });
                
                // Initialize with weekly data
                if (data.weekly && Object.keys(data.weekly).length > 0) {
                    createChart(data.weekly, 'Past 7 Days');
                    document.querySelector('[data-filter="weekly"]').classList.add('active');
                } else if (data.monthly && Object.keys(data.monthly).length > 0) {
                    createChart(data.monthly, 'Past Month');
                    document.querySelector('[data-filter="monthly"]').classList.add('active');
                } else {
                    createChart(data.yearly, 'Past Year');
                    document.querySelector('[data-filter="yearly"]').classList.add('active');
                }
            })
            .catch(error => {
                console.error('Error fetching mood data:', error);
                // Show empty chart
                createChart({}, 'No Data');
            });
    }

    // Form validation
    const authForms = document.querySelectorAll('form');
    authForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const email = form.querySelector('input[type="email"]');
            const password = form.querySelector('input[type="password"]');
            
            if (email && !email.value.includes('@')) {
                e.preventDefault();
                alert('Please enter a valid email address');
                return;
            }
            
            if (password && password.value.length < 6) {
                e.preventDefault();
                alert('Password must be at least 6 characters long');
                return;
            }
        });
    });

    // Button click animations
    document.querySelectorAll('.btn, .option-btn, .welcome-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 100);
        });
    });

    // Smooth transitions for page navigation
    document.querySelectorAll('a[href]').forEach(link => {
        if (!link.href.includes('#') && !link.href.includes('spotify.com')) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                document.body.style.opacity = '0.8';
                setTimeout(() => {
                    window.location.href = this.href;
                }, 200);
            });
        }
    });
});

// Chat message animation
function animateMessage(messageElement) {
    messageElement.style.opacity = '0';
    messageElement.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
        messageElement.style.transition = 'all 0.3s ease';
        messageElement.style.opacity = '1';
        messageElement.style.transform = 'translateY(0)';
    }, 100);
}

// Background animation for welcome page
function createParticles() {
    const container = document.querySelector('.welcome-container');
    if (!container) return;
    
    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.cssText = `
            position: absolute;
            width: 2px;
            height: 2px;
            background: rgba(255, 255, 255, 0.5);
            border-radius: 50%;
            pointer-events: none;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            animation: float ${3 + Math.random() * 4}s ease-in-out infinite;
            animation-delay: ${Math.random() * 2}s;
        `;
        container.appendChild(particle);
    }
}

// CSS for particle animation
const style = document.createElement('style');
style.textContent = `
    @keyframes float {
        0%, 100% { transform: translateY(0px) translateX(0px); }
        25% { transform: translateY(-10px) translateX(5px); }
        50% { transform: translateY(0px) translateX(-5px); }
        75% { transform: translateY(10px) translateX(5px); }
    }
`;
document.head.appendChild(style);

// Initialize particles on welcome page
if (document.querySelector('.welcome-container')) {
    createParticles();
}
