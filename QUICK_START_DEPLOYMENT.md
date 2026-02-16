# 🚀 Quick Start: Deploy in 5 Minutes

## The Fastest Way to Deploy Your Dashboard

---

## Option 1: Automated Deployment (Easiest) ⭐

### Just run this:
```bash
deploy.bat
```

Follow the prompts and you're done!

---

## Option 2: Manual Deployment (5 Steps)

### Step 1: Initialize Git (30 seconds)
```bash
git init
git add .
git commit -m "Smart Bus Dashboard"
```

### Step 2: Create GitHub Repo (1 minute)
1. Go to https://github.com/new
2. Name: `smart-bus-dashboard`
3. Make it **Public**
4. Click "Create repository"

### Step 3: Push Code (1 minute)
```bash
git remote add origin https://github.com/YOUR_USERNAME/smart-bus-dashboard.git
git branch -M main
git push -u origin main
```
*Replace YOUR_USERNAME with your GitHub username*

### Step 4: Deploy on Streamlit (2 minutes)
1. Go to https://share.streamlit.io/
2. Click "New app"
3. Select your repository
4. Main file: `working_dashboard.py`
5. Click "Deploy"

### Step 5: Done! (1 minute)
Wait for build to complete, then access your dashboard at:
```
https://YOUR-APP-NAME.streamlit.app
```

---

## 🎯 That's It!

Your dashboard is now live and accessible worldwide!

---

## 📚 Need More Details?

See the complete guide: `DEPLOYMENT_GUIDE_STREAMLIT_CLOUD.md`

---

## ❓ Common Issues

**Q: Git push asks for password?**  
A: Use a Personal Access Token from https://github.com/settings/tokens

**Q: Deployment fails?**  
A: Check the logs in Streamlit Cloud dashboard

**Q: App won't start?**  
A: Make sure it runs locally first: `streamlit run working_dashboard.py`

---

## 🆘 Need Help?

1. Check `DEPLOYMENT_CHECKLIST.md`
2. Read `DEPLOYMENT_GUIDE_STREAMLIT_CLOUD.md`
3. Visit https://discuss.streamlit.io/

---

**Good luck! 🎉**
