#!/usr/bin/env python3
"""
Cybersecurity News Monitor
Aggregates latest cybersecurity news from multiple trusted sources
Generates structured analysis: Issue, Solution, Cause, Timeline
"""

import feedparser
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# Top Cybersecurity News RSS Feeds
FEEDS = {
    # Major News Sources
    'the_hacker_news': 'https://feeds.feedburner.com/TheHackersNews',
    'bleeping_computer': 'https://www.bleepingcomputer.com/feed/',
    'krebs_on_security': 'https://krebsonsecurity.com/feed/',
    'dark_reading': 'https://www.darkreading.com/rss_simple.asp',
    'security_week': 'https://www.securityweek.com/feed/',
    
    # Threat Intelligence
    'talos_blog': 'https://blog.talosintelligence.com/rss/',
    'recorded_future': 'https://www.recordedfuture.com/feed',
    'threat_post': 'https://threatpost.com/feed/',
    
    # Vendor Blogs
    'sophos_news': 'https://news.sophos.com/en-us/feed/',
    'malwarebytes': 'https://www.malwarebytes.com/blog/feed',
    'crowdstrike_blog': 'https://www.crowdstrike.com/blog/feed/',
    
    # Government & CERT
    'cisa_alerts': 'https://www.cisa.gov/cybersecurity-advisories/all.xml',
    'us_cert': 'https://www.cisa.gov/uscert/ncas/current-activity.xml',
    
    # Specialized
    'cloud_security': 'https://cloudsecurityalliance.org/blog/feed/',
    'sans_reading_room': 'https://www.sans.org/reading-room/rss/',
}

OUTPUT_DIR = Path('cybersecurity_updates')
OUTPUT_DIR.mkdir(exist_ok=True)

def fetch_feed(feed_url, feed_name):
    """Fetch and parse RSS feed"""
    try:
        print(f"Fetching {feed_name} from {feed_url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        feed = feedparser.parse(feed_url, request_headers=headers)
        
        if feed.bozo:
            print(f"Warning: Feed parsing issue for {feed_name}")
            
        return feed
    except Exception as e:
        print(f"Error fetching {feed_name}: {e}")
        return None

def is_recent(published_date, days=3):
    """Check if article is from last N days (default 3 for breaking news)"""
    try:
        if hasattr(published_date, 'timetuple'):
            pub_date = datetime(*published_date.timetuple()[:6])
        else:
            return True
            
        cutoff = datetime.now() - timedelta(days=days)
        return pub_date >= cutoff
    except:
        return True

def clean_html_text(html_text):
    """Remove HTML tags and clean text"""
    text = re.sub(r'<[^>]+>', '', html_text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[\r\n\t]', ' ', text)
    return text.strip()

def extract_key_sentences(text, max_sentences=1):
    """Extract key sentences from text"""
    if not text:
        return None
        
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    if not sentences:
        return None
    
    summary_sentences = sentences[:max_sentences]
    summary = '. '.join(summary_sentences)
    
    if len(summary) > 200:
        summary = summary[:197] + '...'
    elif not summary.endswith('.'):
        summary += '.'
        
    return summary

def categorize_threat(title, content):
    """Categorize the type of cybersecurity threat"""
    title_lower = title.lower()
    content_lower = content.lower() if content else ''
    
    categories = []
    
    threat_types = {
        'Ransomware': ['ransomware', 'ransom', 'lockbit', 'blackcat', 'alphv'],
        'Data Breach': ['data breach', 'leaked', 'exposed database', 'stolen data'],
        'Vulnerability': ['vulnerability', 'cve-', 'zero-day', 'exploit', 'patch'],
        'Malware': ['malware', 'trojan', 'backdoor', 'rootkit', 'botnet'],
        'Phishing': ['phishing', 'spear phishing', 'social engineering', 'credential theft'],
        'APT/Nation-State': ['apt', 'nation-state', 'state-sponsored', 'lazarus', 'apt28'],
        'DDoS': ['ddos', 'denial of service', 'botnet attack'],
        'Supply Chain': ['supply chain', 'third-party', 'vendor compromise'],
        'Cloud Security': ['cloud', 'aws', 'azure', 'gcp', 's3 bucket'],
        'IoT/OT': ['iot', 'industrial', 'scada', 'ot security'],
    }
    
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
    """
    Extract structured information: Issue, Solution, Cause, Timeline, Severity
    """
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
    severity_keywords = {
        'Critical': ['critical', 'severe', 'actively exploited', 'zero-day', 'widespread'],
        'High': ['high severity', 'major breach', 'significant impact', 'urgent'],
        'Medium': ['medium', 'moderate', 'notable'],
        'Low': ['low', 'minor', 'minimal impact']
    }
    
    for severity, keywords in severity_keywords.items():
        for keyword in keywords:
            if keyword in content_lower or keyword in title.lower():
                analysis['severity'] = severity
                break
        if analysis['severity']:
            break
    
    # Extract ISSUE
    issue_keywords = ['vulnerability', 'threat', 'attack', 'breach', 'exploit', 
                      'malware', 'ransomware', 'zero-day', 'flaw', 'bug',
                      'leaked', 'compromised', 'hacked', 'exposed']
    
    for keyword in issue_keywords:
        if keyword in content_lower:
            sentences = re.split(r'[.!?]+', content)
            for sent in sentences:
                if keyword in sent.lower() and len(sent.strip()) > 30:
                    analysis['issue'] = sent.strip()[:250]
                    break
            if analysis['issue']:
                break
    
    if not analysis['issue']:
        analysis['issue'] = title
    
    # Extract SOLUTION/MITIGATION
    solution_keywords = ['patch', 'update', 'fix', 'mitigate', 'remediate',
                        'recommend', 'should', 'advised', 'implement',
                        'security measures', 'protection']
    
    for keyword in solution_keywords:
        if keyword in content_lower:
            sentences = re.split(r'[.!?]+', content)
            for sent in sentences:
                if keyword in sent.lower() and len(sent.strip()) > 30:
                    analysis['solution'] = sent.strip()[:250]
                    break
            if analysis['solution']:
                break
    
    # Extract CAUSE
    cause_keywords = ['caused by', 'due to', 'exploiting', 'leveraging',
                     'abusing', 'vulnerability in', 'flaw in', 'weakness in']
    
    for keyword in cause_keywords:
        if keyword in content_lower:
            idx = content_lower.find(keyword)
            if idx != -1:
                start = max(0, content.rfind('.', 0, idx) + 1)
                end = content.find('.', idx)
                if end != -1:
                    analysis['cause'] = content[start:end].strip()[:250]
                    break
    
    # Extract TIMELINE
    timeline_patterns = [
        r'(discovered|detected|reported|disclosed|announced)\s+(on|in)\s+([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})',
        r'(since|from)\s+([A-Z][a-z]+\s+\d{4})',
        r'(actively exploited|observed)\s+(since|from)\s+(\w+\s+\d{4})',
    ]
    
    for pattern in timeline_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            start = max(0, match.start() - 30)
            end = min(len(content), match.end() + 80)
            analysis['timeline'] = content[start:end].strip()[:200]
            break
    
    return analysis

def extract_article_content(link):
    """Extract article content from webpage"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(link, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        content = None
        
        # Try to find article content
        article = soup.find('article')
        if article:
            paragraphs = article.find_all('p')
            if paragraphs:
                content = ' '.join([p.get_text() for p in paragraphs[:8]])
        
        # Fallback to meta description
        if not content:
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc:
                content = meta_desc.get('content')
        
        return content
    except Exception as e:
        print(f"  Warning: Could not extract content: {e}")
        return None

def generate_summary(title, description, content):
    """Generate concise summary"""
    if description:
        clean_desc = clean_html_text(description)
        summary = extract_key_sentences(clean_desc, max_sentences=1)
        if summary:
            return summary
    
    if content:
        clean_content = clean_html_text(content)
        summary = extract_key_sentences(clean_content, max_sentences=1)
        if summary:
            return summary
    
    return f"Security update: {title}"

def process_feeds():
    """Process all RSS feeds"""
    all_articles = []
    recent_articles = []
    
    for feed_name, feed_url in FEEDS.items():
        feed = fetch_feed(feed_url, feed_name)
        
        if not feed or not hasattr(feed, 'entries'):
            continue
            
        print(f"Found {len(feed.entries)} entries in {feed_name}")
        
        for entry in feed.entries[:15]:  # Process more entries for breaking news
            print(f"  Processing: {entry.get('title', 'No Title')[:60]}...")
            
            description = entry.get('summary', '')
            content = entry.get('content', [{}])[0].get('value', '') if 'content' in entry else ''
            
            # Extract full content for recent articles
            full_content = None
            structured_analysis = None
            
            if hasattr(entry, 'published_parsed') and is_recent(entry.published_parsed, days=3):
                full_content = extract_article_content(entry.get('link', ''))
                if full_content:
                    structured_analysis = analyze_article_structure(
                        entry.get('title', ''),
                        full_content,
                        entry.get('link', '')
                    )
            
            summary = generate_summary(
                entry.get('title', ''),
                description or full_content,
                content
            )
            
            article = {
                'source': feed_name.replace('_', ' ').title(),
                'title': entry.get('title', 'No Title'),
                'link': entry.get('link', ''),
                'published': entry.get('published', 'Unknown'),
                'summary': description,
                'ai_summary': summary,
                'authors': [author.get('name', '') for author in entry.get('authors', [])],
            }
            
            if structured_analysis:
                article['analysis'] = structured_analysis
            
            if hasattr(entry, 'published_parsed') and is_recent(entry.published_parsed, days=3):
                recent_articles.append(article)
                
            all_articles.append(article)
    
    return all_articles, recent_articles

def save_json_report(articles, filename):
    """Save articles as JSON"""
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(articles)} articles to {filepath}")

def generate_markdown_report(recent_articles):
    """Generate Markdown report with structured analysis"""
    md_content = f"""# 🔒 Cybersecurity Latest News

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

## 🚨 Breaking News (Last 3 Days)

"""
    
    if not recent_articles:
        md_content += "*No new articles in the last 3 days.*\n"
    else:
        # Group by threat category
        by_category = {}
        for article in recent_articles:
            categories = article.get('analysis', {}).get('threat_categories', ['General Security'])
            for cat in categories:
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(article)
        
        # Sort by severity
        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, None: 4}
        
        for category in sorted(by_category.keys()):
            articles = by_category[category]
            
            # Sort by date (latest first), then by severity
            def sort_key(article):
                try:
                    pub_date = article.get('published', '')
                    if pub_date and pub_date != 'Unknown':
                        # Try multiple date formats
                        for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%a, %d %b %Y %H:%M:%S %Z', '%Y-%m-%d %H:%M:%S']:
                            try:
                                return (datetime.strptime(pub_date, fmt), 
                                        severity_order.get(article.get('analysis', {}).get('severity'), 4))
                            except:
                                continue
                    return (datetime.min, severity_order.get(article.get('analysis', {}).get('severity'), 4))
                except:
                    return (datetime.min, severity_order.get(article.get('analysis', {}).get('severity'), 4))
            
            articles.sort(key=sort_key, reverse=True)
            
            md_content += f"\n### 🔴 {category}\n\n"
            
            for idx, article in enumerate(articles[:5], 1):  # Top 5 per category
                # Severity badge
                severity = article.get('analysis', {}).get('severity')
                severity_badge = ''
                if severity == 'Critical':
                    severity_badge = '🔴 **CRITICAL**'
                elif severity == 'High':
                    severity_badge = '🟠 **HIGH**'
                elif severity == 'Medium':
                    severity_badge = '🟡 **MEDIUM**'
                
                md_content += f"#### {idx}. [{article['title']}]({article['link']})\n\n"
                
                if severity_badge:
                    md_content += f"{severity_badge}  \n"
                
                md_content += f"**📡 Source:** {article['source']}  \n"
                md_content += f"**📅 Published:** {article['published']}  \n"
                
                # CVEs if present
                cves = article.get('analysis', {}).get('cves', [])
                if cves:
                    md_content += f"**🔖 CVEs:** {', '.join(cves)}  \n"
                
                # Summary
                if article.get('ai_summary'):
                    md_content += f"\n**📝 Summary:** {article['ai_summary']}\n"
                
                # Detailed Analysis
                if article.get('analysis'):
                    analysis = article['analysis']
                    md_content += "\n**🔍 Analysis:**\n\n"
                    
                    if analysis.get('issue'):
                        md_content += f"- **⚠️ Issue:** {analysis['issue']}\n"
                    
                    if analysis.get('cause'):
                        md_content += f"- **🔎 Cause:** {analysis['cause']}\n"
                    
                    if analysis.get('solution'):
                        md_content += f"- **✅ Solution:** {analysis['solution']}\n"
                    
                    if analysis.get('timeline'):
                        md_content += f"- **⏰ Timeline:** {analysis['timeline']}\n"
                
                md_content += "\n---\n\n"
    
    # Add sources section
    md_content += f"""
## 📡 News Sources Monitored

### Major News Outlets
- **The Hacker News**: Breaking cybersecurity news and threat updates
- **Bleeping Computer**: Malware, vulnerabilities, and security guides
- **Krebs on Security**: Investigative cybercrime journalism
- **Dark Reading**: Enterprise security and threat analysis
- **SecurityWeek**: Comprehensive security news coverage

### Threat Intelligence
- **Cisco Talos**: Advanced threat research and intelligence
- **Recorded Future**: Predictive threat intelligence
- **ThreatPost**: Breaking threat news and analysis

### Vendor Blogs
- **Sophos News**: Security research and product updates
- **Malwarebytes Blog**: Malware analysis and removal guides
- **CrowdStrike Blog**: Threat hunting and endpoint security

### Government Sources
- **CISA Alerts**: Official US cybersecurity advisories
- **US-CERT**: Current security activities and alerts

### Specialized
- **Cloud Security Alliance**: Cloud security best practices
- **SANS Reading Room**: Security research and whitepapers

---

*🤖 This report is automatically generated every 4 hours with AI-powered threat analysis.*  
*📊 Includes: Threat categorization, CVE tracking, Severity assessment, Actionable intelligence*  
*Repository: [Cybersecurity News Monitor](https://github.com/starkarthikr/cybersecurity-news-monitor)*
"""
    
    with open('CYBERSECURITY_NEWS.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"Generated Markdown report with {len(recent_articles)} recent articles")

def main():
    print("=" * 70)
    print("Cybersecurity News Monitor - Threat Intelligence Analysis")
    print("=" * 70)
    
    all_articles, recent_articles = process_feeds()
    
    save_json_report(all_articles, 'all_news.json')
    save_json_report(recent_articles, 'recent_news.json')
    
    generate_markdown_report(recent_articles)
    
    analyzed = sum(1 for a in recent_articles if a.get('analysis'))
    critical = sum(1 for a in recent_articles 
                   if a.get('analysis', {}).get('severity') == 'Critical')
    
    print("=" * 70)
    print(f"Total Articles Processed: {len(all_articles)}")
    print(f"Recent Articles (3 days): {len(recent_articles)}")
    print(f"With Structured Analysis: {analyzed}")
    print(f"Critical Severity: {critical}")
    print("=" * 70)

if __name__ == '__main__':
    main()
