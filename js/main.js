// Function to load and convert Markdown content
async function loadMarkdownContent(filePath) {
    try {
        const response = await fetch(filePath);
        if (!response.ok) throw new Error('Failed to load content');
        const markdown = await response.text();
        return marked.parse(markdown);
    } catch (error) {
        console.error('Error loading content:', error);
        return '<p>Error loading content. Please try again later.</p>';
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

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', initializeContent); 