/* ==================== Particle Background Initialization ==================== */

let particlesInitialized = false;

function initializeParticles() {
    if (particlesInitialized) return;
    
    // Use the direct initializer form to pass a config object
    // particlesJS.load expects a URL string; passing an object caused a fetch to '/[object Object]'.
    particlesJS('particles-js', {
        particles: {
            number: { value: 80, density: { enable: true, value_area: 800 } },
            color: { value: "#6366f1" },
            shape: { type: "circle" },
            opacity: { value: 0.3, random: false },
            size: { value: 3, random: true },
            line_linked: {
                enable: true,
                distance: 150,
                color: "#6366f1",
                opacity: 0.2,
                width: 1
            },
            move: {
                enable: true,
                speed: 2,
                direction: "none",
                random: false,
                straight: false,
                out_mode: "out",
                bounce: false
            }
        },
        interactivity: {
            detect_on: "canvas",
            events: {
                onhover: { enable: true, mode: "repulse" },
                onclick: { enable: true, mode: "push" },
                resize: true
            },
            modes: {
                repulse: { distance: 200, duration: 0.4 },
                push: { particles_nb: 4 }
            }
        },
        retina_detect: true
    });
    // particlesJS does not provide a callback when using the direct object initializer,
    // so mark initialized after a short timeout to avoid race conditions in demos.
    setTimeout(() => {
        particlesInitialized = true;
        console.log("Particles initialized successfully");
    }, 250);
}

/* ==================== Theme Management ==================== */

class ThemeManager {
    constructor() {
        this.themeToggle = document.getElementById('theme-toggle');
        this.isDarkMode = true;
        this.init();
    }
    
    init() {
        const savedTheme = localStorage.getItem('skillbridge-theme') || 'dark';
        this.isDarkMode = savedTheme === 'dark';
        this.applyTheme();
        
        this.themeToggle.addEventListener('click', () => this.toggle());
    }
    
    toggle() {
        this.isDarkMode = !this.isDarkMode;
        this.applyTheme();
    }
    
    applyTheme() {
        const body = document.body;
        if (this.isDarkMode) {
            body.classList.remove('light-mode');
            body.classList.add('dark-mode');
            this.themeToggle.textContent = '☀️';
            localStorage.setItem('skillbridge-theme', 'dark');
        } else {
            body.classList.remove('dark-mode');
            body.classList.add('light-mode');
            this.themeToggle.textContent = '🌙';
            localStorage.setItem('skillbridge-theme', 'light');
        }
    }
}

/* ==================== Navigation Management ==================== */

class NavigationManager {
    constructor() {
        this.navLinks = document.querySelectorAll('.nav-link');
        this.init();
    }
    
    init() {
        this.navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.setActive(link);
                const section = link.getAttribute('data-section');
                this.scrollToSection(section);
            });
        });
        
        this.setActive(this.navLinks[0]);
    }
    
    setActive(link) {
        this.navLinks.forEach(l => l.classList.remove('active'));
        link.classList.add('active');
    }
    
    scrollToSection(section) {
        const element = document.getElementById(section);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    }
}

/* ==================== Form Management ==================== */

class FormManager {
    constructor() {
        this.form = document.getElementById('pathway-form');
        this.sliderInput = document.getElementById('time-available');
        this.sliderValue = document.getElementById('slider-value');
        this.API_BASE_URL = 'http://127.0.0.1:5000/api';
        this.init();
    }
    
    init() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        this.sliderInput.addEventListener('input', (e) => {
            this.sliderValue.textContent = e.target.value;
        });
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(this.form);
        const learnerInput = this.buildLearnerInput(formData);
        
        this.showLoader();
        
        try {
            const response = await fetch(`${this.API_BASE_URL}/generate_pathway`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(learnerInput),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.displayResults(data);
            
        } catch (error) {
            console.error('Error generating pathway:', error);
            this.displayError();
        }
    }
    
    buildLearnerInput(formData) {
        const learningStyles = [];
        const constraints = [];
        
        document.querySelectorAll('input[name="learning_style"]:checked').forEach(cb => {
            learningStyles.push(cb.value);
        });
        
        document.querySelectorAll('input[name="constraints"]:checked').forEach(cb => {
            constraints.push(cb.value);
        });
        
        return {
            learner_id: `user_${Date.now()}`,
            career_goal: formData.get('career_goal'),
            time_available_weekly: parseInt(formData.get('time_available_weekly'), 10),
            language_preference: ["English"],
            learning_style: learningStyles.length > 0 ? learningStyles : ["Video lectures"],
            constraints: constraints.length > 0 ? constraints : ["No cost"],
            certification_goals: true
        };
    }
    
    showLoader() {
        const resultsSection = document.getElementById('results-section');
        const resultsContainer = document.getElementById('results-container');
        
        resultsContainer.innerHTML = `
            <div class="loader">
                <div></div>
                <p>🤖 AI Agents analyzing your goals...</p>
                <p style="font-size: 0.875rem; color: var(--text-tertiary); margin-top: 1rem;">
                    • Goal Analyzer: Breaking down your career aspirations<br>
                    • Resource Researcher: Finding the best learning materials<br>
                    • Roadmap Synthesizer: Creating your personalized pathway
                </p>
            </div>
        `;
        
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    displayResults(data) {
        if (data.status !== 'success' || !data.roadmap) {
            this.displayError(data.error || "Could not generate a roadmap. Please try different options.");
            return;
        }
        
        const { roadmap, evaluation_score, job_market_insights } = data;
        
        let resultsHtml = `
            <div class="roadmap" style="animation: slideInUp 0.6s ease-out;">
                <div class="roadmap-header">
                    <h2>✨ ${roadmap.pathway_title}</h2>
                    <p style="color: var(--text-tertiary); margin-top: 0.5rem;">
                        Generated at ${new Date().toLocaleTimeString()}
                    </p>
                </div>
                
                <div class="roadmap-stats">
                    <div class="stat" style="animation: slideInUp 0.6s ease-out 0.1s both;">
                        <h3>🎯 Quality Score</h3>
                        <p>${evaluation_score}/10</p>
                    </div>
                    <div class="stat" style="animation: slideInUp 0.6s ease-out 0.2s both;">
                        <h3>⏱️ Total Hours</h3>
                        <p>${roadmap.total_hours} hrs</p>
                    </div>
                    <div class="stat" style="animation: slideInUp 0.6s ease-out 0.3s both;">
                        <h3>🎓 Primary Goal</h3>
                        <p>${roadmap.primary_goal}</p>
                    </div>
                </div>
        `;
        
        roadmap.phases.forEach((phase, phaseIndex) => {
            resultsHtml += `
                <div class="phase" style="animation: slideInUp 0.6s ease-out ${0.2 + phaseIndex * 0.1}s both;">
                    <div class="phase-header">
                        <h3>📍 ${phase.title}</h3>
                        <p>Duration: ${phase.duration_weeks} weeks</p>
                    </div>
                    <ul class="course-list">
            `;
            
            phase.courses.forEach(course => {
                const platformEmoji = {
                    'Coursera': '📚',
                    'Udemy': '🎬',
                    'Linux Academy': '🐧',
                    'YouTube': '▶️'
                };
                
                const emoji = platformEmoji[course.platform] || '📖';
                
                resultsHtml += `
                    <li class="course">
                        <div class="course-rank">${course.rank}</div>
                        <div class="course-details">
                            <h4>${emoji} ${course.title}</h4>
                            <p>
                                <strong>Platform:</strong> ${course.platform} | 
                                <strong>Duration:</strong> ${course.duration_hours}h | 
                                <strong>Rating:</strong> ⭐ ${course.rating}/5
                            </p>
                        </div>
                    </li>
                `;
            });
            
            resultsHtml += `</ul></div>`;
        });
        
        if (job_market_insights) {
            resultsHtml += `
                <div class="job-market-insights" style="animation: slideInUp 0.6s ease-out 0.5s both;">
                    <h3>💼 Job Market Insights</h3>
                    <div class="insights-grid">
                        <div class="insight-card">
                            <h4>Role</h4>
                            <p>${job_market_insights.role}</p>
                        </div>
                        <div class="insight-card">
                            <h4>Demand Trend</h4>
                            <p>${job_market_insights.demand_trend}</p>
                        </div>
                        <div class="insight-card">
                            <h4>Market Growth</h4>
                            <p>${job_market_insights.market_growth}</p>
                        </div>
                        <div class="insight-card">
                            <h4>Avg Salary (India)</h4>
                            <p>${job_market_insights.avg_salary_india}</p>
                        </div>
                    </div>
                </div>
            `;
        }
        
        resultsHtml += '</div>';
        
        const resultsContainer = document.getElementById('results-container');
        resultsContainer.innerHTML = resultsHtml;
        
        setTimeout(() => {
            resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }
    
    displayError(message = "An unexpected error occurred. Please try again later.") {
        const resultsContainer = document.getElementById('results-container');
        resultsContainer.innerHTML = `
            <div class="error-message" style="animation: slideInUp 0.6s ease-out;">
                <h3 style="color: var(--danger); margin-bottom: 0.5rem;">❌ Error</h3>
                <p>${message}</p>
            </div>
        `;
    }
}

/* ==================== Scroll Animations ==================== */

class ScrollAnimationManager {
    constructor() {
        this.observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        this.observer = new IntersectionObserver(this.handleIntersection, this.observerOptions);
        this.init();
    }
    
    init() {
        document.querySelectorAll('.section-title, .section-subtitle, .feature-card, .stat').forEach(el => {
            this.observer.observe(el);
        });
    }
    
    handleIntersection = (entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'slideInUp 0.8s ease-out forwards';
                this.observer.unobserve(entry.target);
            }
        });
    }
}

/* ==================== Application Initialization ==================== */

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 SkillBridge Application Loading...');
    
    initializeParticles();
    
    const themeManager = new ThemeManager();
    const navigationManager = new NavigationManager();
    const formManager = new FormManager();
    const pathwaysManager = new PathwaysManager();
    const scrollAnimationManager = new ScrollAnimationManager();
    
    console.log('✅ SkillBridge Application Initialized');
    
    document.body.style.opacity = '1';
});

/* ==================== Pathways Management ==================== */

class PathwaysManager {
    constructor() {
        this.button = document.getElementById('load-pathways');
        this.list = document.getElementById('pathways-list');
        this.API_BASE_URL = 'http://127.0.0.1:5000/api';
        this.init();
    }

    init() {
        if (!this.button) return;
        this.button.addEventListener('click', () => this.loadRecent());
    }

    async loadRecent() {
        if (!this.list) return;
        this.list.innerHTML = '<p style="text-align:center; color: var(--text-tertiary);">Loading recent pathways…</p>';
        try {
            const res = await fetch(`${this.API_BASE_URL}/pathways/recent?limit=8`);
            if (!res.ok) {
                if (res.status === 401) {
                    this.list.innerHTML = '<p style="text-align:center; color: var(--text-tertiary);">Please log in to view private pathways.</p>';
                    return;
                }
                throw new Error(`HTTP ${res.status}`);
            }

            const body = await res.json();
            this.renderList(body.pathways || []);
        } catch (err) {
            console.error('Error loading pathways', err);
            this.list.innerHTML = `<p style="text-align:center; color: var(--danger);">Could not load pathways: ${err.message}</p>`;
        }
    }

    renderList(pathways) {
        if (!pathways || pathways.length === 0) {
            this.list.innerHTML = '<p style="text-align:center; color: var(--text-tertiary);">No pathways found.</p>';
            return;
        }

        const items = pathways.map(p => {
            const title = p.roadmap?.pathway_title || `Pathway for ${p.learner_id || 'unknown'}`;
            const score = p.evaluation_score ?? '—';
            const created = p.created_at ? new Date(p.created_at).toLocaleString() : '';
            return `
                <div class="pathway-card" style="margin-bottom:1rem; padding:1rem; background: rgba(255,255,255,0.02); border:1px solid rgba(99,102,241,0.06); border-radius:8px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <h3 style="margin:0">${title}</h3>
                            <p style="margin:0; color:var(--text-tertiary); font-size:0.9rem;">${created}</p>
                        </div>
                        <div style="text-align:right">
                            <div style="font-weight:700; color:var(--primary);">Score: ${score}</div>
                            <button class="cta-button" style="margin-top:0.5rem; padding:0.4rem 0.6rem;" data-id="${p._id || ''}">View</button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        this.list.innerHTML = items;
        // Attach view handlers if needed
        this.list.querySelectorAll('.cta-button').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.currentTarget.dataset.id;
                if (!id) return;
                window.location.hash = `#pathways`;
                // Try to open pathway detail via API
                alert('Open pathway detail is not implemented in the demo. Pathway id: ' + id);
            });
        });
    }
}

/* ==================== Utility Functions ==================== */

window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.background = 'rgba(15, 23, 42, 0.95)';
        navbar.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.2)';
    } else {
        navbar.style.background = 'rgba(15, 23, 42, 0.8)';
        navbar.style.boxShadow = 'none';
    }
});

const originalFetch = window.fetch;
window.fetch = function(...args) {
    const [resource] = args;
    if (typeof resource === 'string' && resource.includes('/api/')) {
        console.log(`📡 API Call: ${resource}`);
    }
    return originalFetch.apply(this, args);
};

document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('pathway-form').scrollIntoView({ behavior: 'smooth' });
    }
});

console.log('SkillBridge script loaded successfully!');
