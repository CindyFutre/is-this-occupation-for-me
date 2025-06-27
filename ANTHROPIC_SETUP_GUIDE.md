# 🤖 Anthropic Claude API Setup Guide

## Overview
Your job analysis system now uses a **Hybrid Analysis Engine** that provides:
- **🎯 Primary Mode**: Anthropic Claude/Sonnet 4.0 for superior AI-powered analysis
- **🔧 Fallback Mode**: Enhanced rule-based analysis when API key isn't available

## Current Status
✅ **System is working** - Currently using enhanced rule-based analysis  
⚠️ **API Key needed** - To unlock Claude/Sonnet 4.0 superior analysis

## Step 1: Create Anthropic Account

1. **Visit**: https://console.anthropic.com
2. **Sign up** using one of these options:
   - Continue with Google (recommended)
   - Enter your email address
3. **Verify** your email if using email signup
4. **Complete** account setup

## Step 2: Get Your API Key

1. **Login** to Anthropic Console
2. **Navigate** to API Keys section (usually in left sidebar)
3. **Click** "Create Key" or "New API Key"
4. **Name** your key (e.g., "Occupation100-Analysis")
5. **Copy** the API key (starts with `sk-ant-api03-...`)
6. **Store safely** - you won't see it again!

## Step 3: Configure Your System

1. **Open** your `.env` file: `backend/.env`
2. **Replace** the placeholder:
   ```bash
   # Change this line:
   ANTHROPIC_API_KEY="your-anthropic-api-key-here"
   
   # To your actual key:
   ANTHROPIC_API_KEY="sk-ant-api03-[your-actual-key-here]"
   ```
3. **Save** the file
4. **Restart** your backend server (it will auto-reload)

## Step 4: Verify Claude Integration

When you restart the server, look for this message:
```
✅ Claude/Sonnet 4.0 initialized successfully - Using AI-powered analysis
```

Instead of:
```
ℹ️ No Anthropic API key configured - Using enhanced rule-based analysis
```

## API Pricing (Very Affordable)

**Claude 3.5 Sonnet Pricing:**
- **Input**: $3.00 per million tokens
- **Output**: $15.00 per million tokens

**Estimated Cost per Job Analysis:**
- **200 job postings analysis**: ~$0.10-0.30 per analysis
- **Monthly usage** (50 analyses): ~$5-15/month

## Benefits of Claude Integration

### 🎯 **Superior Analysis Quality**
- **Intelligent synthesis** across 200+ job postings
- **Context-aware categorization** of responsibilities vs skills
- **Natural language understanding** of job requirements
- **Industry-specific terminology** recognition

### 🔍 **Better Data Extraction**
- **Semantic understanding** of job descriptions
- **Automatic normalization** of similar terms
- **Contextual relevance** scoring
- **Reduced noise** and artifacts

### 📊 **Enhanced Results**
- **More accurate categorization** (Responsibilities, Skills, Qualifications, Unique Aspects)
- **Better frequency counting** across multiple postings
- **Cleaner context sentences** for each extracted term
- **Industry-specific insights**

## Fallback System Features

Even without Claude, your system provides:
- ✅ **Enhanced rule-based analysis** with 100+ normalization rules
- ✅ **Industry-specific patterns** for electrical, healthcare, tech roles
- ✅ **Intelligent categorization** using keyword scoring
- ✅ **Activity extraction** with context sentences
- ✅ **Full functionality** - all features work

## Testing Your Setup

1. **Search** for any job title (e.g., "Electrician")
2. **Check server logs** for analysis mode confirmation
3. **Compare results** quality before/after Claude integration
4. **Monitor** API usage in Anthropic Console

## Troubleshooting

### ❌ "Claude initialization failed"
- **Check** API key format (should start with `sk-ant-api03-`)
- **Verify** key is active in Anthropic Console
- **Ensure** no extra spaces in `.env` file

### ❌ "API rate limit exceeded"
- **Wait** a few minutes and try again
- **Check** your Anthropic Console usage limits
- **Consider** upgrading your Anthropic plan

### ❌ "Invalid API key"
- **Regenerate** key in Anthropic Console
- **Update** `.env` file with new key
- **Restart** backend server

## Support

- **Anthropic Documentation**: https://docs.anthropic.com
- **API Reference**: https://docs.anthropic.com/claude/reference
- **Console**: https://console.anthropic.com

---

**Ready to upgrade to Claude/Sonnet 4.0 analysis? Follow the steps above! 🚀**