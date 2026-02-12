#!/usr/bin/env python3
"""
Cybersecurity News Monitor
Aggregates latest cybersecurity news from multiple trusted sources
Generates structured analysis: Issue, Solution, Cause, Timeline
"""

import feedparser
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import socket

# Set global socket timeout as fallback
socket.setdefaulttimeout(15)

# Top Cybersecurity News RSS Feeds
FEEDS = {
    'the_hacker_news': 'https://feeds.feedburner.com/TheHackersNews',
    'bleeping_computer': 'https://www.bleepingcomputer.com/feed/',
    'krebs_on_security': 'https://krebsonsecurity.com/feed/',
    'dark_reading': 'https://www.darkreading.com/rss_simple.asp',
    'security_week': 'https://www.securityweek.com/feed/',
    'talos_blog': 'https://blog.talosintelligence.com/rss/',
    'recorded_future': 'https://www.recordedfuture.com/feed',
    'threat_post': 'https://threatpost.com/feed/',
    'sophos_news': 'https://news.sophos.com/en-us/feed/',
    'malwarebytes': 'https://www.malwarebytes.com/blog/feed',
    'crowdstrike_blog': 'https://www.crowdstrike.com/blog/feed/',
    'cisa_alerts': 'https://www.cisa.gov/cybersecurity-advisories/all.xml',
    'us_cert': 'https://www.cisa.gov/uscert/ncas/current-activity.xml',
}

OUTPUT_DIR = Path('cybersecurity_updates')
OUTPUT_DIR.mkdir(exist_ok=True)

# Timeout settings (in seconds)
FEED_TIMEOUT = 10
CONTENT_TIMEOUT = 8
MAX_RETRIES = 2


def fetch_feed(feed_url, feed_name):
    """Fetch and parse RSS feed with timeout"""
    try:
        print(f'Fetching {feed_name} from {feed_url}')
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        # Use requests with timeout first, then pass to feedparser
        try:
            response = requests.get(feed_url, headers=headers, timeout=FEED_TIMEOUT)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
        except requests.exceptions.Timeout:
            print(f'Timeout error for {feed_name} - skipping')
            return None
        except requests.exceptions.RequestException as e:
            print(f'Request error for {feed_name}: {e} - skipping')
            return None
        
        if feed.bozo:
            print(f'Warning: Feed parsing issue for {feed_name}')
        
        return feed
    except Exception as e:
        print(f'Error fetching {feed_name}: {e} - skipping')
        return None


def is_recent(published_date, days=3):
    """Check if article is recent"""
    try:
        if hasattr(published_date, 'timetuple'):
            pub_date = datetime(*published_date.timetuple()[:6], tzinfo=timezone.utc)
        else:
            return True
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return pub_date >= cutoff
    except Exception:
        return True


def clean_html_text(html_text):
    """Remove HTML tags and clean text"""
    text = re.sub(r'<[^>]+>', '', html_text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_key_sentences(text, max_sentences=1):
    """Extract key sentences from text"""
    if not text:
        return None
    
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    if not sentences:
        return None
    
    summary = '. '.join(sentences[:max_sentences])
    
    if len(summary) > 200:
        summary = summary[:197] + '...'
    elif not summary.endswith('.'):
        summary += '.'
    
    return summary


def categorize_threat(title, content):
    """Categorize the type of cybersecurity threat"""
    title_lower = title.lower()
    content_lower = content.lower() if content else ''
    
    threat_types = {
        'Ransomware': ['ransomware', 'ransom', 'lockbit', 'blackcat'],
        'Data Breach': ['data breach', 'leaked', 'exposed database'],
        'Vulnerability': ['vulnerability', 'cve-', 'zero-day', 'exploit'],
        'Malware': ['malware', 'trojan', 'backdoor', 'botnet'],
        'Phishing': ['phishing', 'spear phishing', 'credential theft'],
        'APT': ['apt', 'nation-state', 'lazarus'],
        'DDoS': ['ddos', 'denial of service'],
        'Supply Chain': ['supply chain', 'third-party'],
    }
    
    categories = []
    for category, keywords in threat_types.items():
        for keyword in keywords:
            if keyword in title_lower or keyword in content_lower:
                categories.append(category)
                break
    
    return categories if categories else ['General Security']


def extract_cve_ids(text):
    """Extract CVE identifiers from text"""
    if not text:
        return []
    
    cve_pattern = r'CVE-\d{4}-\d{4,7}'
    return list(set(re.findall(cve_pattern, text, re.IGNORECASE)))


def analyze_article_structure(title, content, link):
    """Extract structured information from article"""
    analysis = {
        'issue': None,
        'solution': None,
        'cause': None,
        'timeline': None,
        'severity': None,
        'cves': [],
        'threat_categories': []
    }
    
    if not content:
        return analysis
    
    content_lower = content.lower()
    
    # Extract CVEs
    analysis['cves'] = extract_cve_ids(title + ' ' + content)
    
    # Categorize threat
    analysis['threat_categories'] = categorize_threat(title, content)
    
    # Determine severity
    if any(keyword in content_lower for keyword in ['critical', 'severe', 'zero-day']):
        analysis['severity'] = 'Critical'
    elif any(keyword in content_lower for keyword in ['high', 'major', 'urgent']):
        analysis['severity'] = 'High'
    elif any(keyword in content_lower for keyword in ['medium', 'moderate']):
        analysis['severity'] = 'Medium'
    else:
        analysis['severity'] = 'Low'
    
    # Extract ISSUE
    sentences = re.split(r'[.!?]+', content)
    for sent in sentences:
        if len(sent.strip()) > 30:
            analysis['issue'] = sent.strip()[:250]
            break
    
    if not analysis['issue']:
        analysis['issue'] = title
    
    return analysis


def extract_article_content(link):
    """Extract article content from webpage with timeout"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(link, headers=headers, timeout=CONTENT_TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find article content
        article = soup.find('article')
        if article:
            paragraphs = article.find_all('p')
            if paragraphs:
                return ' '.join([p.get_text() for p in paragraphs[:8]])
        
        # Fallback to meta description
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            return meta_desc.get('content')
        
        return None
    except requests.exceptions.Timeout:
        print(f'Timeout extracting content from {link[:50]}... - skipping')
        return None
    except requests.exceptions.RequestException as e:
        print(f'Request error extracting content: {e} - skipping')
        return None
    except Exception as e:
        print(f'Warning: Could not extract content: {e}')
        return None


def process_feeds():
    """Process all RSS feeds with error handling"""
    all_articles = []
    recent_articles = []
    
    successful_feeds = 0
    failed_feeds = 0
    
    for feed_name, feed_url in FEEDS.items():
        try:
            feed = fetch_feed(feed_url, feed_name)
            
            if not feed or not hasattr(feed, 'entries'):
                failed_feeds += 1
                continue
            
            print(f'Found {len(feed.entries)} entries in {feed_name}')
            successful_feeds += 1
            
            for entry in feed.entries[:10]:
                try:
                    description = entry.get('summary', '')
                    title = entry.get('title', 'No Title')
                    link = entry.get('link', '')
                    published = entry.get('published', 'Unknown')
                    
                    # Extract full content for recent articles (with timeout)
                    full_content = None
                    structured_analysis = None
                    
                    if hasattr(entry, 'published_parsed') and is_recent(entry.published_parsed, days=3):
                        try:
                            full_content = extract_article_content(link)
                            if full_content:
                                structured_analysis = analyze_article_structure(title, full_content, link)
                        except Exception as e:
                            print(f'Error analyzing article: {e} - continuing')
                    
                    article = {
                        'source': feed_name.replace('_', ' ').title(),
                        'title': title,
                        'link': link,
                        'published': published,
                        'summary': description,
                    }
                    
                    if structured_analysis:
                        article['analysis'] = structured_analysis
                    
                    if hasattr(entry, 'published_parsed') and is_recent(entry.published_parsed, days=3):
                        recent_articles.append(article)
                    
                    all_articles.append(article)
                except Exception as e:
                    print(f'Error processing entry in {feed_name}: {e} - continuing')
                    continue
        except Exception as e:
            print(f'Fatal error processing feed {feed_name}: {e} - skipping')
            failed_feeds += 1
            continue
    
    print(f'\nFeed Summary: {successful_feeds} successful, {failed_feeds} failed')
    return all_articles, recent_articles


def save_json_report(articles, filename):
    """Save articles as JSON"""
    try:
        filepath = OUTPUT_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f'Saved {len(articles)} articles to {filepath}')
    except Exception as e:
        print(f'Error saving JSON: {e}')


def generate_markdown_report(recent_articles):
    """Generate Markdown report with structured analysis"""
    try:
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        md_content = f"# Cybersecurity Latest News\n\n**Last Updated:** {timestamp}\n\n## Breaking News (Last 3 Days)\n\n"
        
        if not recent_articles:
            md_content += "*No new articles in the last 3 days.*\n"
        else:
            for idx, article in enumerate(recent_articles, 1):
                title = article.get('title', 'No Title')
                link = article.get('link', '')
                source = article.get('source', 'Unknown')
                published = article.get('published', 'Unknown')
                
                md_content += f"### {idx}. [{title}]({link})\n\n"
                md_content += f"**Source:** {source}  \n"
                md_content += f"**Published:** {published}  \n"
                
                # Add analysis if available
                if article.get('analysis'):
                    analysis = article['analysis']
                    if analysis.get('severity'):
                        md_content += f"**Severity:** {analysis['severity']}  \n"
                    if analysis.get('cves'):
                        md_content += f"**CVEs:** {', '.join(analysis['cves'])}  \n"
                    if analysis.get('threat_categories'):
                        cats = ', '.join(analysis['threat_categories'])
                        md_content += f"**Categories:** {cats}  \n"
                
                md_content += "\n---\n\n"
        
        with open('CYBERSECURITY_NEWS.md', 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f'Generated Markdown report with {len(recent_articles)} articles')
    except Exception as e:
        print(f'Error generating markdown report: {e}')


def main():
    """Main function"""
    print("=" * 70)
    print("Cybersecurity News Monitor - Threat Intelligence Analysis")
    print("=" * 70)
    
    all_articles, recent_articles = process_feeds()
    
    save_json_report(all_articles, 'all_news.json')
    save_json_report(recent_articles, 'recent_news.json')
    generate_markdown_report(recent_articles)
    
    print("=" * 70)
    print(f"Total Articles Processed: {len(all_articles)}")
    print(f"Recent Articles (3 days): {len(recent_articles)}")
    print("=" * 70)


if __name__ == '__main__':
    main()
