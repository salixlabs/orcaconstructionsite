#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path
from datetime import datetime
import re

def calculate_root_path(output_path):
    """Calculate the relative path back to root based on output file location"""
    parts = Path(output_path).parent.parts
    if not parts:
        return ""
    return "../" * len(parts)

def estimate_read_time(markdown_content):
    """Estimate reading time in minutes based on word count"""
    words = len(re.findall(r'\w+', markdown_content))
    minutes = max(1, round(words / 200))  # Assuming 200 words per minute
    return f"{minutes} min read"

def get_post_metadata(markdown_path):
    """Extract metadata from markdown file"""
    try:
        with open(markdown_path, 'r') as f:
            content = f.read()
            
        # Extract title from first h1
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else "Untitled"
        
        # Extract first paragraph for description
        desc_match = re.search(r'\n\n([^#\n].+?)\n\n', content, re.DOTALL)
        description = desc_match.group(1) if desc_match else ""
        description = re.sub(r'\s+', ' ', description).strip()[:160]
        
        # Get file modification time for publish date
        mtime = os.path.getmtime(markdown_path)
        publish_date = datetime.fromtimestamp(mtime)
        
        return {
            "title": title,
            "description": description,
            "author": "Orca Construction",
            "publish_date": publish_date.isoformat(),
            "display_date": publish_date.strftime("%B %d, %Y"),
            "read_time": estimate_read_time(content)
        }
    except Exception as e:
        print(f"Warning: Error extracting metadata: {e}")
        return {}

def get_blog_navigation(current_post):
    """Get previous and next post navigation"""
    posts_dir = Path("content/blog")
    if not posts_dir.exists():
        return "", ""
        
    posts = sorted([p for p in posts_dir.glob("*.md")], key=lambda p: p.stat().st_mtime, reverse=True)
    try:
        current_idx = [p.stem for p in posts].index(Path(current_post).stem)
        
        prev_post = ""
        if current_idx < len(posts) - 1:
            prev_metadata = get_post_metadata(posts[current_idx + 1])
            prev_post = f'''<a href="{posts[current_idx + 1].stem}.html" class="prev-post">
                ← {prev_metadata.get("title", "Previous Post")}
            </a>'''
            
        next_post = ""
        if current_idx > 0:
            next_metadata = get_post_metadata(posts[current_idx - 1])
            next_post = f'''<a href="{posts[current_idx - 1].stem}.html" class="next-post">
                {next_metadata.get("title", "Next Post")} →
            </a>'''
            
        return prev_post, next_post
    except ValueError:
        return "", ""

def get_related_posts(current_post, max_posts=3):
    """Get related posts based on recency"""
    posts_dir = Path("content/blog")
    if not posts_dir.exists():
        return ""
        
    posts = sorted([p for p in posts_dir.glob("*.md") if p.stem != Path(current_post).stem],
                  key=lambda p: p.stat().st_mtime, reverse=True)
    
    related_html = []
    for post in posts[:max_posts]:
        metadata = get_post_metadata(post)
        related_html.append(f'''
            <article class="related-post">
                <h4><a href="{post.stem}.html">{metadata.get("title", "Untitled")}</a></h4>
                <div class="blog-meta">
                    <span class="publish-date">{metadata.get("display_date", "")}</span>
                    <span class="read-time">{metadata.get("read_time", "")}</span>
                </div>
            </article>
        ''')
    
    return "\n".join(related_html)

def generate_page(template_path, output_path, config):
    """Generate a new page from the template"""
    with open(template_path, 'r') as f:
        template = f.read()
    
    root_path = calculate_root_path(output_path)
    css_path = root_path + "css/"
    
    # For blog posts, get additional metadata and navigation
    if template_path.endswith("blog-post.html"):
        markdown_path = config.get("markdown_path", "")
        if markdown_path:
            metadata = get_post_metadata(markdown_path)
            config.update(metadata)
            
            # Add navigation and related posts
            prev_post, next_post = get_blog_navigation(markdown_path)
            config["prev_post"] = prev_post
            config["next_post"] = next_post
            config["related_posts"] = get_related_posts(markdown_path)
            
            # Add current URL for sharing
            config["current_url"] = f"https://www.orca.construction/blog/posts/{Path(output_path).name}"
    
    # Basic replacements
    replacements = {
        "<!-- PAGE_TITLE -->": config.get("title", ""),
        "<!-- ROOT_PATH -->": root_path,
        "<!-- CSS_PATH -->": css_path,
        "<!-- ADDITIONAL_HEAD -->": config.get("additional_head", ""),
        "<!-- MAIN_CONTENT -->": config.get("main_content", ""),
        "<!-- ADDITIONAL_SCRIPTS -->": config.get("additional_scripts", ""),
        "<!-- MARKDOWN_PATH -->": config.get("markdown_path", ""),
        "<!-- META_DESCRIPTION -->": config.get("description", ""),
        "<!-- META_AUTHOR -->": config.get("author", ""),
        "<!-- PUBLISH_DATE -->": config.get("publish_date", ""),
        "<!-- DISPLAY_DATE -->": config.get("display_date", ""),
        "<!-- READ_TIME -->": config.get("read_time", ""),
        "<!-- CURRENT_URL -->": config.get("current_url", ""),
        "<!-- PREV_POST -->": config.get("prev_post", ""),
        "<!-- NEXT_POST -->": config.get("next_post", ""),
        "<!-- RELATED_POSTS -->": config.get("related_posts", "")
    }
    
    content = template
    for key, value in replacements.items():
        content = content.replace(key, str(value))
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir:  # Only create directory if path has a directory component
        os.makedirs(output_dir, exist_ok=True)
    
    # Write the generated page
    with open(output_path, 'w') as f:
        f.write(content)

def regenerate_all_pages():
    """Regenerate all pages using the template system"""
    pages = [
        {
            "template": "templates/base.html",
            "output": "index.html",
            "config": {
                "title": "Building Dreams, Delivering Excellence",
                "main_content": get_index_content()
            }
        },
        {
            "template": "templates/base.html",
            "output": "contact.html",
            "config": {
                "title": "Contact Us",
                "main_content": get_contact_content(),
                "additional_scripts": '<script src="js/contact.js"></script>'
            }
        },
        {
            "template": "templates/base.html",
            "output": "faq.html",
            "config": {
                "title": "FAQ",
                "main_content": get_faq_content(),
                "additional_scripts": '<script src="js/faq.js"></script>'
            }
        },
        {
            "template": "templates/base.html",
            "output": "blog/index.html",
            "config": {
                "title": "Blog",
                "main_content": get_blog_index_content(),
                "additional_scripts": '<script src="../js/newsletter.js"></script>'
            }
        }
    ]
    
    # Add blog posts
    posts_dir = Path("content/blog")
    if posts_dir.exists():
        for post in posts_dir.glob("*.md"):
            pages.append({
                "template": "templates/blog-post.html",
                "output": f"blog/posts/{post.stem}.html",
                "config": {
                    "markdown_path": str(post)
                }
            })
    
    for page in pages:
        print(f"Generating {page['output']}...")
        generate_page(page["template"], page["output"], page["config"])

def get_index_content():
    """Return the main content for index page"""
    return '''
        <section class="hero">
            <h1>Building Dreams,<br>Delivering Excellence</h1>
            <p>We combine innovative design with sustainable practices to create spaces that inspire.</p>
            <p class="subtitle">Your vision, our expertise – let's build something extraordinary together.</p>
        </section>

        <section class="services">
            <h2>Our Expertise</h2>
            <div class="services-grid">
                <div class="service-card">
                    <h3>Residential Construction</h3>
                    <p>Creating dream homes with attention to detail and sustainable practices. From custom builds to renovations, we bring your vision to life.</p>
                </div>
                <div class="service-card">
                    <h3>Commercial Projects</h3>
                    <p>Modern, efficient spaces for businesses to thrive. We specialize in office spaces, retail locations, and commercial renovations.</p>
                </div>
                <div class="service-card">
                    <h3>Sustainable Building</h3>
                    <p>Leading the way in eco-friendly construction. We implement green building practices and energy-efficient solutions.</p>
                </div>
            </div>
        </section>

        <section class="newsletter-section">
            <h2>Stay Updated</h2>
            <p>Subscribe to our newsletter for the latest construction insights, project updates, and sustainable building practices.</p>
            <form class="newsletter-form">
                <input type="email" placeholder="Enter your email address" required>
                <button type="submit">Subscribe</button>
                <div class="form-status"></div>
            </form>
        </section>
    '''

def get_blog_index_content():
    """Return the main content for blog index page"""
    return '''
        <section class="blog-header">
            <h1>Construction Insights</h1>
            <p>Expert advice and industry updates from Orca Construction</p>
        </section>

        <section class="blog-grid">
            <article class="blog-card">
                <div class="blog-card-content">
                    <h2><a href="posts/sustainable-construction.html">Sustainable Construction Practices</a></h2>
                    <div class="blog-meta">January 19, 2024 • 5 min read</div>
                    <p>Learn about the latest sustainable construction practices and how they're shaping the future of building.</p>
                    <a href="posts/sustainable-construction.html" class="read-more">Read More →</a>
                </div>
            </article>

            <article class="blog-card">
                <div class="blog-card-content">
                    <h2><a href="posts/home-renovation-tips.html">Essential Home Renovation Tips</a></h2>
                    <div class="blog-meta">January 15, 2024 • 4 min read</div>
                    <p>Planning a home renovation? Here are the essential tips you need to know before getting started.</p>
                    <a href="posts/home-renovation-tips.html" class="read-more">Read More →</a>
                </div>
            </article>

            <article class="blog-card">
                <div class="blog-card-content">
                    <h2><a href="posts/commercial-construction-trends.html">Commercial Construction Trends 2024</a></h2>
                    <div class="blog-meta">January 10, 2024 • 6 min read</div>
                    <p>Discover the latest trends shaping commercial construction in 2024 and beyond.</p>
                    <a href="posts/commercial-construction-trends.html" class="read-more">Read More →</a>
                </div>
            </article>
        </section>

        <section class="newsletter-section">
            <h2>Stay Updated with Our Latest News</h2>
            <p>Subscribe to our newsletter for the latest construction insights, sustainable building practices, and project updates.</p>
            <form class="newsletter-form">
                <input type="email" placeholder="Enter your email address" required>
                <button type="submit">Subscribe</button>
                <div class="form-status"></div>
            </form>
        </section>
    '''

def get_contact_content():
    """Return the main content for contact page"""
    return '''
        <section class="contact-header">
            <h1>Get in Touch</h1>
            <p>Let's discuss your construction project</p>
        </section>

        <section class="contact-container">
            <div class="contact-info">
                <h2>Contact Information</h2>
                <div class="info-item">
                    <h3>Address</h3>
                    <p>123 Construction Way<br>Seattle, WA 98101</p>
                </div>
                <div class="info-item">
                    <h3>Phone</h3>
                    <p>(555) 123-4567</p>
                </div>
                <div class="info-item">
                    <h3>Email</h3>
                    <p>info@orca.construction</p>
                </div>
                <div class="info-item">
                    <h3>Hours</h3>
                    <p>Monday - Friday: 8am - 5pm<br>Saturday: 9am - 2pm</p>
                </div>
            </div>

            <form class="contact-form" id="contactForm">
                <div class="form-group">
                    <label for="name">Full Name</label>
                    <input type="text" id="name" name="name" required>
                </div>

                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" required>
                </div>

                <div class="form-group">
                    <label for="phone">Phone Number</label>
                    <input type="tel" id="phone" name="phone">
                </div>

                <div class="form-group">
                    <label for="projectType">Project Type</label>
                    <select id="projectType" name="projectType" required>
                        <option value="">Select a project type</option>
                        <option value="residential">Residential Construction</option>
                        <option value="commercial">Commercial Construction</option>
                        <option value="renovation">Renovation</option>
                        <option value="other">Other</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="message">Project Details</label>
                    <textarea id="message" name="message" rows="5" required></textarea>
                </div>

                <button type="submit" class="submit-button">Send Message</button>
            </form>
        </section>
    '''

def get_faq_content():
    """Return the main content for FAQ page"""
    return '''
        <section class="faq-header">
            <h1>Frequently Asked Questions</h1>
            <p>Find answers to common questions about our construction services</p>
        </section>

        <section class="faq-container">
            <div class="faq-group">
                <h2>General Questions</h2>
                
                <div class="faq-item">
                    <button class="faq-question">
                        How long has Orca Construction been in business?
                        <span class="faq-icon">+</span>
                    </button>
                    <div class="faq-answer">
                        <p>Orca Construction has been serving the Seattle area since 2024. While we're a new company, our team brings over 30 years of combined experience in residential and commercial construction.</p>
                    </div>
                </div>

                <div class="faq-item">
                    <button class="faq-question">
                        Are you licensed and insured?
                        <span class="faq-icon">+</span>
                    </button>
                    <div class="faq-answer">
                        <p>Yes, we are fully licensed, bonded, and insured in Washington state. We maintain comprehensive coverage to protect our clients and our work.</p>
                    </div>
                </div>
            </div>

            <div class="faq-group">
                <h2>Project Planning</h2>
                
                <div class="faq-item">
                    <button class="faq-question">
                        How do you handle project estimates?
                        <span class="faq-icon">+</span>
                    </button>
                    <div class="faq-answer">
                        <p>We provide detailed, transparent estimates that break down all costs. Our team conducts thorough site visits and consultations to ensure accurate pricing and timeline estimates.</p>
                    </div>
                </div>

                <div class="faq-item">
                    <button class="faq-question">
                        What types of projects do you handle?
                        <span class="faq-icon">+</span>
                    </button>
                    <div class="faq-answer">
                        <p>We specialize in:</p>
                        <ul>
                            <li>Custom home construction</li>
                            <li>Commercial building projects</li>
                            <li>Home renovations and remodels</li>
                            <li>Sustainable building solutions</li>
                        </ul>
                    </div>
                </div>
            </div>
        </section>

        <section class="faq-cta">
            <h2>Still have questions?</h2>
            <p>We're here to help with any additional questions you might have about your construction project.</p>
            <a href="contact.html" class="cta-button">Contact Us</a>
        </section>
    '''

def main():
    if len(sys.argv) < 2:
        print("No arguments provided. Regenerating all pages...")
        regenerate_all_pages()
        return
    
    if len(sys.argv) < 3:
        print("Usage: generate_page.py <output_path> <title> [--blog]")
        sys.exit(1)
    
    output_path = sys.argv[1]
    title = sys.argv[2]
    is_blog = "--blog" in sys.argv
    
    template_path = "templates/blog-post.html" if is_blog else "templates/base.html"
    config = {"title": title}
    
    if is_blog:
        markdown_path = f"content/blog/{Path(output_path).stem}.md"
        config["markdown_path"] = markdown_path
    
    generate_page(template_path, output_path, config)
    print(f"Generated page at {output_path}")

if __name__ == "__main__":
    main() 