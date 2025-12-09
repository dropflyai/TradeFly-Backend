/**
 * TradeFly Multi-Page App
 * Main application entry point with SPA routing
 */

// Define routes
const routes = {
    '/': {
        template: '/static/pages/scalping.html',
        init: null  // Scalping page has its own init
    },
    '/scalping': {
        template: '/static/pages/scalping.html',
        init: null
    },
    '/swing': {
        template: '/static/pages/swing.html',
        init: null
    },
    '/monitor': {
        template: '/static/pages/monitor.html',
        init: null
    },
    '/paper-lab': {
        template: '/static/pages/paper-lab.html',
        init: null
    },
    '/watchlist': {
        template: '/static/pages/watchlist.html',
        init: null
    }
};

// Application initialization
async function initApp() {
    console.log('TradeFly AI - Initializing...');

    try {
        // Load navigation bar
        await loadNavigation();

        // Initialize router
        const router = new Router(routes);

        console.log('✅ TradeFly AI - Ready');
    } catch (error) {
        console.error('Error initializing app:', error);
    }
}

// Load navigation bar component
async function loadNavigation() {
    try {
        const response = await fetch('/static/components/navbar.html');
        const html = await response.text();

        // Insert navbar at the top of the body
        document.body.insertAdjacentHTML('afterbegin', html);

        console.log('✅ Navigation loaded');
    } catch (error) {
        console.error('Error loading navigation:', error);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}
