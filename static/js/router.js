/**
 * Simple SPA Router for TradeFly
 * Handles navigation between pages without full reload
 */

class Router {
    constructor(routes) {
        this.routes = routes;
        this.currentPage = null;
        this.init();
    }

    init() {
        // Handle browser back/forward
        window.addEventListener('popstate', () => this.loadRoute());

        // Handle link clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-link]')) {
                e.preventDefault();
                this.navigate(e.target.getAttribute('href'));
            }
        });

        // Load initial route
        this.loadRoute();
    }

    navigate(path) {
        // Push to history
        history.pushState({}, '', path);
        this.loadRoute();
    }

    async loadRoute() {
        const path = window.location.pathname;
        const route = this.routes[path] || this.routes['/'];

        if (!route) {
            console.error(`No route found for ${path}`);
            return;
        }

        // Show loading state
        const appContainer = document.getElementById('app');
        if (appContainer) {
            appContainer.innerHTML = '<div class="loading">Loading...</div>';
        }

        try {
            // Load page template
            const response = await fetch(route.template);
            const html = await response.text();

            if (appContainer) {
                // Create temporary container to parse HTML
                const temp = document.createElement('div');
                temp.innerHTML = html;

                // Extract script tags before setting innerHTML
                const scripts = temp.querySelectorAll('script');
                const scriptContents = [];
                scripts.forEach(script => {
                    scriptContents.push(script.textContent);
                    script.remove(); // Remove from temp so it doesn't get added to DOM
                });

                // Set HTML without scripts
                appContainer.innerHTML = temp.innerHTML;

                // Execute scripts manually
                scriptContents.forEach(scriptContent => {
                    try {
                        // Execute in global scope
                        const scriptElement = document.createElement('script');
                        scriptElement.textContent = scriptContent;
                        document.body.appendChild(scriptElement);
                        document.body.removeChild(scriptElement);
                    } catch (err) {
                        console.error('Error executing page script:', err);
                    }
                });
            }

            // Update active nav
            this.updateActiveNav(path);

            // Run page initialization
            if (route.init && typeof route.init === 'function') {
                await route.init();
            }

            this.currentPage = path;
            console.log(`Loaded page: ${path}`);
        } catch (error) {
            console.error('Error loading route:', error);
            if (appContainer) {
                appContainer.innerHTML = '<div class="error">Error loading page</div>';
            }
        }
    }

    updateActiveNav(path) {
        // Remove active class from all nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        // Add active class to current nav link
        const activeLink = document.querySelector(`.nav-link[href="${path}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }
}

// Export for use in main app
window.Router = Router;
