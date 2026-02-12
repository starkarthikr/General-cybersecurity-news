import requests
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# OpenRouter API configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# SECURITY: API key must be provided via environment variable
# Never hardcode API keys in source code!
API_KEY = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("API_KEY")

if not API_KEY:
    print("❌ ERROR: OPENROUTER_API_KEY environment variable is not set!")
    print("\nPlease set your OpenRouter API key:")
    print("  - For local development: Add to .env file")
    print("  - For GitHub Actions: Add as repository secret")
    print("\nGet your API key from: https://openrouter.ai/keys")
    sys.exit(1)

# Reliable Free Models for Cybersecurity Analysis
FREE_MODELS = {
    "1": {"name": "meta-llama/llama-3.2-3b-instruct:free", "desc": "Llama 3.2 3B - Best for news summaries"},
    "2": {"name": "google/gemma-2-9b-it:free", "desc": "Gemma 2 9B - Great for threat analysis"},
    "3": {"name": "qwen/qwen-2.5-7b-instruct:free", "desc": "Qwen 2.5 7B - Excellent for technical details"},
    "4": {"name": "mistralai/mistral-7b-instruct:free", "desc": "Mistral 7B - Best for vulnerability reports"},
    "5": {"name": "microsoft/phi-3-mini-128k-instruct:free", "desc": "Phi-3 Mini - Good for long reports"},
}

FALLBACK_MODELS = [
    "meta-llama/llama-3.2-3b-instruct:free",
    "google/gemma-2-9b-it:free",
    "mistralai/mistral-7b-instruct:free",
    "qwen/qwen-2.5-7b-instruct:free",
]

# Timeout settings (in seconds)
CONNECT_TIMEOUT = 10  # Time to establish connection
READ_TIMEOUT = 30     # Time to receive response
REQUEST_TIMEOUT = (CONNECT_TIMEOUT, READ_TIMEOUT)

def create_session_with_retries():
    """Create requests session with retry logic and timeouts"""
    session = requests.Session()
    retry_strategy = Retry(
        total=2,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def generate_content(prompt: str, model: str = "meta-llama/llama-3.2-3b-instruct:free", retry_fallback: bool = True) -> dict:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/starkarthikr/General-cybersecurity-news",
        "X-Title": "Cybersecurity News Monitor"
    }
    
    models_to_try = [model]
    if retry_fallback:
        for fallback in FALLBACK_MODELS:
            if fallback != model and fallback not in models_to_try:
                models_to_try.append(fallback)
    
    session = create_session_with_retries()
    
    for attempt, current_model in enumerate(models_to_try, 1):
        try:
            print(f"\n🔍 Analyzing cybersecurity news... (Attempt {attempt}/{len(models_to_try)})")
            print(f"   Model: {current_model}")
            print(f"   Timeout: {CONNECT_TIMEOUT}s connect, {READ_TIMEOUT}s read")
            print(f"   Query: {prompt[:100]}..." if len(prompt) > 100 else f"   Query: {prompt}")
            
            payload = {
                "model": current_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = session.post(
                API_URL, 
                json=payload, 
                headers=headers, 
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 429:
                print(f"\n⚠️ Rate limited on {current_model}")
                if attempt < len(models_to_try):
                    print(f"   Retrying with fallback model...")
                    time.sleep(2)
                    continue
                else:
                    return {"success": False, "content": "", "error": "All models rate limited", "model_used": None}
            
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                print(f"\n❌ API Error: {error_msg}")
                if attempt < len(models_to_try):
                    print(f"   Trying fallback model...")
                    time.sleep(1)
                    continue
                return {"success": False, "content": "", "error": error_msg, "model_used": None}
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            print(f"\n✅ Analysis complete! Generated {len(content)} characters.")
            if attempt > 1:
                print(f"   🔄 Used fallback model after {attempt-1} attempt(s)")
            print()
            
            return {"success": True, "content": content, "error": None, "model_used": current_model}
            
        except requests.exceptions.Timeout as e:
            error_msg = f"Timeout error after {CONNECT_TIMEOUT + READ_TIMEOUT}s: {str(e)}"
            print(f"\n⏱️ {error_msg}")
            if attempt < len(models_to_try):
                print(f"   Trying fallback model...")
                time.sleep(1)
                continue
            return {"success": False, "content": "", "error": error_msg, "model_used": None}
        
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error: {str(e)[:100]}"
            print(f"\n🔌 {error_msg}")
            if attempt < len(models_to_try):
                print(f"   Trying fallback model...")
                time.sleep(1)
                continue
            return {"success": False, "content": "", "error": error_msg, "model_used": None}
        
        except Exception as e:
            error_msg = f"Exception: {str(e)[:200]}"
            print(f"\n❌ Error: {error_msg}")
            if attempt < len(models_to_try):
                print(f"   Trying fallback model...")
                time.sleep(1)
                continue
            return {"success": False, "content": "", "error": error_msg, "model_used": None}
    
    session.close()
    return {"success": False, "content": "", "error": "All retry attempts failed", "model_used": None}

def save_output(prompt: str, content: str, model: str) -> str:
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp}-security-report.md"
    filepath = output_dir / filename
    
    markdown_content = f"""# Cybersecurity Analysis Report

**Generated:** {datetime.now().strftime("%B %d, %Y at %I:%M %p IST")}
**AI Model:** `{model}`
**Report Type:** Automated Security Intelligence

---

## Query

{prompt}

---

## Analysis

{content}

---

*Generated by [Cybersecurity News Monitor](https://github.com/starkarthikr/General-cybersecurity-news)*  
*Powered by [OpenRouter AI](https://openrouter.ai) - 100% FREE models*
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return str(filepath)

def update_index():
    output_dir = Path("reports")
    if not output_dir.exists():
        return
    
    files = [f for f in output_dir.glob("*.md") if f.name != "INDEX.md"]
    files = sorted(files, reverse=True)
    
    if not files:
        return
    
    index_content = f"""# Security Reports Index

**Last Updated:** {datetime.now().strftime("%B %d, %Y at %I:%M %p IST")}
**Total Reports:** {len(files)}

---

## All Security Reports

"""
    
    for file in files:
        date_str = file.stem.replace('-security-report', '')
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d_%H-%M-%S")
            formatted_date = date_obj.strftime("%B %d, %Y at %I:%M %p")
        except:
            formatted_date = date_str
        
        index_content += f"- [{formatted_date}]({file.name})\n"
    
    with open(output_dir / "INDEX.md", 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"\n📄 Index updated: reports/INDEX.md ({len(files)} reports)")

if __name__ == "__main__":
    print("=" * 80)
    print("    🔒 CYBERSECURITY NEWS MONITOR - AI-POWERED ANALYSIS 🔒")
    print("=" * 80)
    
    is_github_actions = os.environ.get('GITHUB_ACTIONS') == 'true'
    custom_prompt = os.environ.get('CUSTOM_PROMPT', '')
    custom_model = os.environ.get('CUSTOM_MODEL', 'meta-llama/llama-3.2-3b-instruct:free')
    
    if is_github_actions and custom_prompt:
        print("\n🤖 Running automated security monitoring")
        prompts = [custom_prompt]
        model = custom_model
    elif not is_github_actions:
        print("\n💻 Running in interactive mode\n")
        
        use_custom = input("Use custom security query? (y/n): ").strip().lower()
        
        if use_custom == 'y':
            user_prompt = input("\nEnter your security query: ")
            prompts = [user_prompt]
        else:
            prompts = [
                "Summarize the top 5 critical cybersecurity vulnerabilities discovered this week with CVE numbers, affected systems, and recommended mitigations",
                "Analyze the latest ransomware trends and provide actionable defense strategies for enterprise environments",
                "Generate a threat intelligence report on emerging APT groups and their tactics, techniques, and procedures (TTPs)"
            ]
        
        print("\n" + "="*80)
        print("🔒 AVAILABLE AI MODELS FOR SECURITY ANALYSIS")
        print("="*80)
        for key, model_info in FREE_MODELS.items():
            print(f"{key:>2}. {model_info['desc']}")
        print("="*80)
        
        model_choice = input("\nSelect model (1-5, default=1): ").strip() or "1"
        model = FREE_MODELS.get(model_choice, FREE_MODELS["1"])["name"]
        
    else:
        print("\n⏰ Running scheduled security monitoring")
        prompts = [
            "Generate a comprehensive daily cybersecurity threat report for February 12, 2026, covering critical vulnerabilities, active threats, and security advisories",
        ]
        model = custom_model
    
    print(f"\n🔍 Generating {len(prompts)} security report(s)...")
    print(f"🎯 Primary Model: {model}")
    print(f"🔄 Auto-fallback enabled")
    print(f"⏱️  Timeout: {CONNECT_TIMEOUT}s connect + {READ_TIMEOUT}s read")
    print("="*80)
    
    success_count = 0
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n\n{'='*80}")
        print(f"[SECURITY REPORT #{i} of {len(prompts)}]")
        print(f"{'='*80}")
        print(f"\n🔍 Query: {prompt}\n")
        
        result = generate_content(prompt, model, retry_fallback=True)
        
        if result['success']:
            print("\n" + "-" * 80)
            print("🔒 SECURITY ANALYSIS:")
            print("-" * 80)
            print(result['content'])
            print("-" * 80)
            
            filepath = save_output(prompt, result['content'], result['model_used'])
            print(f"\n✅ Report saved: {filepath}")
            success_count += 1
        else:
            print(f"\n❌ Failed to generate report: {result['error']}")
    
    if success_count > 0:
        update_index()
    
    print("\n" + "="*80)
    print(f"\n🎉 COMPLETE! Successfully generated {success_count}/{len(prompts)} reports.")
    print(f"\n📂 Check the 'reports/' folder for analysis.")
    print(f"📊 View index: reports/INDEX.md")
    print(f"\n🔒 100% FREE AI-powered cybersecurity intelligence!\n")
    print("="*80)
