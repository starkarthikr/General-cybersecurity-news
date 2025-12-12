# Cybersecurity News Monitor 🔒

Automated cybersecurity threat intelligence and news monitoring powered by AI. Daily security reports, vulnerability analysis, and threat assessments using **100% FREE** OpenRouter AI models.

## 🚀 Features

- **Daily Threat Reports** - Automated cybersecurity news summaries
- **Vulnerability Analysis** - CVE tracking and mitigation strategies
- **Threat Intelligence** - APT groups, malware, and attack patterns
- **Zero-Day Monitoring** - Latest exploit discoveries and patches
- **Security Advisories** - Critical alerts and recommendations
- **100% FREE AI Models** - No API costs, unlimited generation
- **Automatic Scheduling** - Daily reports at midnight IST
- **Smart Retry Logic** - Auto-fallback across 5 AI models

## 📁 Repository Structure

```
cybersecurity-news-monitor/
├── main.py                          # AI-powered security analysis engine
├── .github/workflows/
│   └── security-monitor.yml         # Automated workflow
├── reports/                         # Generated security reports
│   ├── INDEX.md                     # Chronological report index
│   └── YYYY-MM-DD_HH-MM-SS-security-report.md
└── README.md                        # This file
```

## 🔧 Quick Start

### Run Locally

```bash
# Clone the repository
git clone https://github.com/starkarthikr/cybersecurity-news-monitor
cd cybersecurity-news-monitor

# Install dependencies
pip install requests

# Run security analysis
python main.py
```

### Run via GitHub Actions

1. Go to **Actions** tab
2. Select **"Cybersecurity News Monitor"**
3. Click **"Run workflow"**
4. Choose your query type:
   - Daily threat report
   - Vulnerability analysis
   - Ransomware trends
   - Custom security query
5. Click **"Run workflow"**

## 📊 Example Queries

### Daily Threat Report
```
Generate a comprehensive daily cybersecurity threat report for [date] covering critical vulnerabilities, active threats, security advisories, and recommended actions
```

### Vulnerability Analysis
```
Analyze the top 10 critical CVEs from this week with CVSS scores, affected systems, exploit availability, and detailed mitigation steps
```

### Ransomware Intelligence
```
Provide a detailed analysis of recent ransomware campaigns including attack vectors, encryption methods, ransom demands, and recovery strategies
```

### Zero-Day Tracking
```
Summarize all zero-day vulnerabilities disclosed this month with CVE IDs, affected vendors, proof-of-concept availability, and patches
```

### APT Group Analysis
```
Generate threat intelligence on emerging APT groups, their TTPs, target sectors, malware families, and attribution indicators
```

### Phishing Campaign Report
```
Analyze current phishing trends, impersonated brands, delivery methods, malicious payloads, and detection rules
```

## 🤖 Available AI Models

All models are **100% FREE** on OpenRouter:

| Model | Best For | Speed | Quality |
|-------|----------|-------|----------|
| **Llama 3.2 3B** | Daily summaries | ⚡⚡⚡ Fast | ⭐⭐⭐ Good |
| **Gemma 2 9B** | Threat analysis | ⚡⚡ Medium | ⭐⭐⭐⭐ Great |
| **Qwen 2.5 7B** | Technical details | ⚡⚡ Medium | ⭐⭐⭐⭐ Great |
| **Mistral 7B** | Vulnerability reports | ⚡⚡ Medium | ⭐⭐⭐⭐ Great |
| **Phi-3 Mini** | Long reports | ⚡ Slower | ⭐⭐⭐ Good |

## 🔒 Security Report Format

Each generated report includes:

- **Timestamp** - Date and time of analysis
- **AI Model Used** - Which model generated the analysis
- **Query** - Original security question
- **Analysis** - Detailed threat intelligence
- **Metadata** - Source attribution

## ⏰ Automated Scheduling

- **Daily Reports:** Runs automatically at **12:00 AM IST** (18:30 UTC)
- **Manual Trigger:** Run anytime via GitHub Actions
- **Smart Retry:** Automatically tries 5 models if one is rate-limited
- **Auto-Commit:** Reports automatically saved to repository

## 📊 View Reports

### Browse on GitHub
1. Navigate to [`reports/`](./reports) folder
2. Check [`reports/INDEX.md`](./reports/INDEX.md) for chronological list
3. Click any report to view full analysis

### Clone and Read Locally
```bash
git pull origin main
cd reports
ls -lt  # View newest reports first
cat 2025-12-13_00-00-00-security-report.md
```

## 🛡️ Use Cases

- **SOC Teams** - Daily threat intelligence briefings
- **Security Researchers** - Vulnerability tracking and analysis
- **IT Administrators** - Patch management and mitigation strategies
- **Pen Testers** - Latest exploit techniques and tools
- **CISO/Leadership** - Executive security summaries
- **Incident Response** - Threat actor TTP documentation

## 🚀 Advanced Usage

### Custom Security Queries

```python
# Example: Track specific threat actor
prompt = "Analyze Lazarus Group's latest campaigns in 2025, including malware variants, C2 infrastructure, and blockchain-related attacks"

# Example: Industry-specific threats
prompt = "Generate a security report for healthcare sector covering HIPAA compliance risks, ransomware targeting hospitals, and medical device vulnerabilities"

# Example: Technical deep-dive
prompt = "Provide detailed analysis of Log4Shell exploitation techniques, vulnerable versions, detection methods, and complete remediation steps"
```

### Integration Ideas

- **Slack/Discord Bot** - Auto-post daily reports
- **Email Digest** - Send reports via email
- **RSS Feed** - Subscribe to security updates
- **SIEM Integration** - Feed threat intel to SIEM
- **Threat Intel Platform** - Export to MISP, ThreatConnect

## ⚠️ Disclaimer

This tool provides AI-generated threat intelligence summaries. Always:

- **Verify information** from official sources (CISA, CVE, vendor advisories)
- **Cross-reference** multiple threat intelligence sources
- **Test mitigations** in controlled environments first
- **Follow** your organization's security policies
- **Consult** cybersecurity professionals for critical decisions

AI-generated content may contain inaccuracies or outdated information.

## 🔗 Resources

- [OpenRouter AI](https://openrouter.ai) - Free AI API provider
- [NIST NVD](https://nvd.nist.gov/) - Vulnerability database
- [CISA Alerts](https://www.cisa.gov/news-events/cybersecurity-advisories) - Government advisories
- [MITRE ATT&CK](https://attack.mitre.org/) - Threat actor TTPs
- [CVE Details](https://www.cvedetails.com/) - Vulnerability information

## 🤝 Contributing

Contributions welcome! Ideas:

- Add more security query templates
- Integrate with threat intelligence APIs
- Create visualization dashboards
- Add export formats (PDF, JSON, CSV)
- Implement sentiment analysis on threats

## 📜 License

MIT License - Free to use and modify

---

**🔒 Stay Secure. Stay Informed. Stay Automated.**

*Powered by [OpenRouter AI](https://openrouter.ai) - 100% FREE Cybersecurity Intelligence*
