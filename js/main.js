// Function to load and convert Markdown content
async function loadMarkdownContent() {
    const markdownContainer = document.getElementById('markdown-content');
    if (!markdownContainer) return;

    const markdownPath = markdownContainer.dataset.markdown;
    if (!markdownPath) return;

    try {
        const response = await fetch(`/${markdownPath}`);
        if (!response.ok) {
            throw new Error(`Failed to load content: ${response.status} ${response.statusText}`);
        }
        
        const markdownText = await response.text();
        const htmlContent = marked.parse(markdownText);
        markdownContainer.innerHTML = htmlContent;
    } catch (error) {
        console.error('Error loading markdown content:', error);
        markdownContainer.innerHTML = '<p>Error loading content. Please try again later.</p>';
    }
}

// Function to initialize content on pages that use Markdown
async function initializeContent() {
    const contentElement = document.getElementById('markdown-content');
    if (!contentElement) return;

    const markdownPath = contentElement.dataset.markdown;
    if (!markdownPath) return;

    const htmlContent = await loadMarkdownContent(markdownPath);
    contentElement.innerHTML = htmlContent;
}

// Mobile Navigation
function initMobileNav() {
    const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
    const nav = document.querySelector('nav');
    const navLinks = document.querySelectorAll('nav ul a');

    if (mobileNavToggle) {
        mobileNavToggle.addEventListener('click', () => {
            mobileNavToggle.classList.toggle('active');
            nav.classList.toggle('active');
            document.body.classList.toggle('nav-open');
        });

        // Close menu when clicking a link
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileNavToggle.classList.remove('active');
                nav.classList.remove('active');
                document.body.classList.remove('nav-open');
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!nav.contains(e.target) && !mobileNavToggle.contains(e.target)) {
                mobileNavToggle.classList.remove('active');
                nav.classList.remove('active');
                document.body.classList.remove('nav-open');
            }
        });
    }
}

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeContent();
    initMobileNav();
    loadMarkdownContent();
}); 