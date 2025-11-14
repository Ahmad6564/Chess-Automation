# Hugging Face API Setup Guide

## 🚀 Quick Setup

The project now uses **Hugging Face Inference API** instead of downloading models locally!

### Benefits:
✅ **No model downloads** - No 4GB+ downloads  
✅ **No GPU needed** - Runs on any machine  
✅ **Faster startup** - Instant initialization  
✅ **Lower memory** - ~100MB vs 4-8GB  
✅ **Always updated** - Latest model version  

---

## 📝 Step 1: Get Your API Token

1. Go to [Hugging Face Settings](https://huggingface.co/settings/tokens)
2. Click **"New token"**
3. Give it a name (e.g., "chess-agent")
4. Select **"Read"** access
5. Click **"Generate token"**
6. Copy the token (starts with `hf_...`)

---

## 🔧 Step 2: Set the Token

### Option A: Environment Variable (Recommended)

**Windows (PowerShell):**
```powershell
$env:HF_API_TOKEN="hf_your_token_here"
```

**Windows (CMD):**
```cmd
set HF_API_TOKEN=hf_your_token_here
```

**Linux/Mac:**
```bash
export HF_API_TOKEN="hf_your_token_here"
```

### Option B: Config File

Edit [`config.yaml`](config.yaml ):
```yaml
vision_model:
  model_name: "Qwen/Qwen2-VL-2B-Instruct"
  api_token: "hf_your_token_here"  # Add your token here
```

---

## ✅ Step 3: Verify Setup

```bash
python quick_test.py
```

Should output:
```
✓ HF API token found
✓ API connection successful
```

---

## 🎮 Step 4: Run the Agent

```bash
# Setup board region
python main.py --setup

# Run the agent
python main.py
```

---

## 📊 API Limits

**Free Tier:**
- 30,000 requests/month
- ~1,000 chess games
- More than enough for personal use

**Rate Limits:**
- 1 request per second (plenty for chess)

---

## 🔒 Security Note

Keep your API token private! Don't commit it to Git.

Add to `.gitignore`:
```
config.yaml
.env
```

---

## ❓ Troubleshooting

**"Model is loading" error:**
- Wait 20 seconds, it will retry automatically
- First request to a model may take longer

**"Invalid token" error:**
- Check token starts with `hf_`
- Verify token is active at huggingface.co/settings/tokens

**"Rate limit" error:**
- Wait 1 second between moves (humanizer does this automatically)

---

## 🆓 Cost: **FREE!**

Hugging Face Inference API is **completely free** for personal use!