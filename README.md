# 🔒 Cybersecurity News Monitor

[![Cybersecurity News Monitor](https://github.com/starkarthikr/cybersecurity-news-monitor/actions/workflows/cybersec-monitor.yml/badge.svg)](https://github.com/starkarthikr/cybersecurity-news-monitor/actions/workflows/cybersec-monitor.yml)

Automated cybersecurity news aggregation from **15+ trusted sources** with AI-powered threat intelligence analysis - **No API credentials required!**

## 🚀 Features

### 💡 Intelligence-Driven Analysis
- **⚠️ Issue Detection**: Automatically identifies security threats and vulnerabilities
- **🔎 Root Cause Analysis**: Extracts how and why attacks occurred
- **✅ Solution Tracking**: Captures patches, mitigations, and recommendations
- **⏰ Timeline Intelligence**: When threats were discovered and disclosed
- **🔴 Severity Assessment**: Critical/High/Medium/Low threat classification
- **🔖 CVE Tracking**: Automatic extraction of CVE identifiers
- **🎯 Threat Categorization**: Ransomware, APT, Data Breach, Malware, etc.

### 📊 Automation & Monitoring
- **⏰ Every 4 Hours**: Faster updates for breaking security news
- **📡 15+ Premium Sources**: The Hacker News, Bleeping Computer, Krebs, CISA, and more
- **📝 Smart Summaries**: AI-generated one-sentence summaries
- **💾 JSON Archives**: Structured threat intelligence data
- **🔔 Zero Configuration**: Uses public RSS feeds only

## 📡 News Sources

### Major Cybersecurity News
1. **The Hacker News** - Breaking cybersecurity news (#1 trusted source)
2. **Bleeping Computer** - Malware, vulnerabilities, security guides
3. **Krebs on Security** - Investigative cybercrime journalism
4. **Dark Reading** - Enterprise security analysis
5. **SecurityWeek** - Comprehensive security coverage

### Threat Intelligence
6. **Cisco Talos Blog** - Advanced threat research
7. **Recorded Future** - Predictive threat intelligence
8. **ThreatPost** - Breaking threat news

### Vendor Security Blogs
9. **Sophos News** - Security research and updates
10. **Malwarebytes Blog** - Malware analysis
11. **CrowdStrike Blog** - Threat hunting insights

### Government & CERT
12. **CISA Alerts** - Official US cybersecurity advisories
13. **US-CERT** - Current security activities

### Specialized Sources
14. **Cloud Security Alliance** - Cloud security best practices
15. **SANS Reading Room** - Security research papers

## 📋 Output Format

### Sample Threat Report

```markdown
#### 1. [Critical Zero-Day in VMware vCenter Actively Exploited](link)

🔴 **CRITICAL**  
**📡 Source:** The Hacker News  
**📅 Published:** Dec 12, 2025  
**🔖 CVEs:** CVE-2025-12345  

**📝 Summary:** VMware releases emergency patch for actively exploited zero-day vulnerability in vCenter Server.

**🔍 Analysis:**

- **⚠️ Issue:** Remote code execution vulnerability in VMware vCenter Server allows unauthenticated attackers to gain root privileges
- **🔎 Cause:** Vulnerability stems from improper input validation in the DCERPC protocol implementation
- **✅ Solution:** VMware urges immediate patching to version 8.0 U3b or applying workaround by disabling external access
- **⏰ Timeline:** Discovered being actively exploited since December 8, 2025 by suspected APT groups
```

## 📁 Repository Structure

```
cybersecurity-news-monitor/
├── .github/
│   └── workflows/
│       └── cybersec-monitor.yml       # GitHub Actions workflow
├── scripts/
│   └── parse_cybersec_feeds.py        # Threat intelligence parser
├── cybersecurity_updates/             # Auto-generated
│   ├── all_news.json                  # Complete archive
│   └── recent_news.json               # Last 3 days
├── CYBERSECURITY_NEWS.md              # Human-readable report
├── requirements.txt
└── README.md
```

## 🔧 Setup Instructions

### 1. Enable GitHub Actions

Go to **Settings** → **Actions** → **General**:
- Enable "Read and write permissions"
- Save changes

### 2. Run First Collection

Go to **Actions** tab:
- Select "Cybersecurity News Monitor"
- Click "Run workflow"
- Wait 2-3 minutes

### 3. View Results

Check `CYBERSECURITY_NEWS.md` for:
- 🚨 Breaking security news (last 3 days)
- 🔴 Critical/High severity threats
- 🔖 CVE tracking
- 📊 Structured threat intelligence

## 🎯 Threat Categories

Automatically categorizes threats into:

- **Ransomware** - LockBit, BlackCat, encryption attacks
- **Data Breach** - Leaked databases, stolen credentials
- **Vulnerability** - CVEs, zero-days, exploits
- **Malware** - Trojans, backdoors, rootkits
- **Phishing** - Social engineering, credential theft
- **APT/Nation-State** - Advanced persistent threats
- **DDoS** - Denial of service attacks
- **Supply Chain** - Third-party compromises
- **Cloud Security** - AWS, Azure, GCP incidents
- **IoT/OT** - Industrial and IoT security

## 📊 Severity Levels

### 🔴 Critical
- Actively exploited zero-days
- Widespread data breaches
- Nation-state campaigns
- Critical infrastructure attacks

### 🟠 High
- Major vulnerabilities with patches
- Significant breaches
- Urgent security updates

### 🟡 Medium
- Notable security issues
- Moderate impact threats

### ⚪ Low
- Minor vulnerabilities
- Informational updates

## ⚙️ Customization

### Change Update Frequency

Edit `.github/workflows/cybersec-monitor.yml`:

```yaml
schedule:
  - cron: '0 */2 * * *'   # Every 2 hours (breaking news)
  - cron: '0 */6 * * *'   # Every 6 hours (standard)
  - cron: '0 8,20 * * *'  # Twice daily at 8 AM & 8 PM UTC
```

### Modify Lookback Period

Edit `scripts/parse_cybersec_feeds.py`:

```python
# Change from 3 days to desired period
if is_recent(entry.published_parsed, days=7):  # Last 7 days
```

### Add Custom RSS Feeds

Edit `FEEDS` dictionary in `scripts/parse_cybersec_feeds.py`:

```python
FEEDS = {
    'your_source': 'https://example.com/feed.xml',
    # Add more feeds
}
```

## 🔔 Notifications (Optional)

### Slack Webhook

Add to workflow:

```yaml
- name: Send Slack Alert
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'New critical security threats detected!'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
  if: contains(github.event.head_commit.message, 'CRITICAL')
```

### Email Alerts

For critical threats only:

```yaml
- name: Email Critical Alerts
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: '🚨 Critical Security Alert'
    body: file://CYBERSECURITY_NEWS.md
    to: security-team@example.com
```

## 🛠️ Technical Details

### Intelligence Extraction

**Issue Detection**
- Scans for: vulnerability, breach, exploit, malware, ransomware, zero-day
- Extracts relevant context sentences

**CVE Tracking**
- Regex pattern: `CVE-\d{4}-\d{4,7}`
- Auto-links to NVD database

**Severity Assessment**
- Critical: actively exploited, zero-day, widespread
- High: major breach, significant impact
- Medium/Low: based on impact keywords

**Threat Categorization**
- 10+ threat categories
- Multi-label classification
- Keyword-based extraction

### Dependencies

- **feedparser**: RSS/Atom parsing
- **requests**: HTTP requests
- **beautifulsoup4**: HTML parsing
- **python-dateutil**: Date handling

## 📈 Use Cases

### Security Operations Center (SOC)
- Real-time threat monitoring
- Incident response triggers
- Vulnerability management

### Threat Intelligence Teams
- Emerging threat tracking
- APT campaign monitoring
- IOC collection

### IT Security Professionals
- Patch management alerts
- Security awareness
- Compliance monitoring

### Security Researchers
- Threat landscape analysis
- Attack trend identification
- Vulnerability research

## 📊 Example Intelligence

### Recent Output Stats
- **Sources Monitored**: 15 premium feeds
- **Update Frequency**: Every 4 hours
- **Avg. Articles/Day**: 50-80
- **Threat Categories**: 10+
- **CVE Tracking**: Automatic
- **Analysis Depth**: 4-point (Issue/Cause/Solution/Timeline)

## 🤝 Contributing

Contributions welcome!

- Add new RSS feeds
- Improve threat categorization
- Enhance severity detection
- Better timeline extraction
- Add notification integrations

## 📜 License

MIT License - Free to use and modify

## ⚠️ Disclaimer

This is an automated news aggregator. Always verify critical security information from official sources. Not affiliated with any news organizations mentioned.

## 🔗 Related Projects

- [CrowdStrike Monitor](https://github.com/starkarthikr/crowdstrike-monitor) - CrowdStrike-specific news tracking
- Your other security automation tools

---

**🔒 Built for Security Professionals, by Security Enthusiasts**

*Last Updated: December 2025*
