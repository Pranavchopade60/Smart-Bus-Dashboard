# ✅ Deployment Checklist

## Before You Deploy

### 1. Prerequisites
- [ ] GitHub account created (https://github.com/signup)
- [ ] Git installed on your computer
- [ ] Dashboard working locally (`streamlit run working_dashboard.py`)

### 2. Project Files
- [ ] `working_dashboard.py` exists
- [ ] `requirements.txt` exists
- [ ] `config.json` exists
- [ ] `src/` folder with all source code
- [ ] `outputs/` folder with data files
- [ ] `.gitignore` file created

### 3. Test Locally
- [ ] Dashboard runs without errors
- [ ] All visualizations display correctly
- [ ] Parameter controls work
- [ ] Data loads properly
- [ ] No sensitive data in code (passwords, API keys)

---

## Deployment Steps

### Step 1: Prepare Git Repository
```bash
# Run these commands in your project folder
git init
git add .
git commit -m "Initial commit: Smart Bus Dashboard"
```
- [ ] Git repository initialized
- [ ] Files committed

### Step 2: Create GitHub Repository
1. Go to https://github.com
2. Click "+" → "New repository"
3. Name: `smart-bus-dashboard`
4. Visibility: **Public** (required for free tier)
5. Don't initialize with README
6. Click "Create repository"

- [ ] GitHub repository created
- [ ] Repository URL copied

### Step 3: Push to GitHub
```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/smart-bus-dashboard.git
git branch -M main
git push -u origin main
```
- [ ] Code pushed to GitHub
- [ ] Repository visible on GitHub

**OR use the automated script:**
```bash
deploy.bat
```

### Step 4: Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"
4. Fill in:
   - Repository: `YOUR_USERNAME/smart-bus-dashboard`
   - Branch: `main`
   - Main file: `working_dashboard.py`
5. Click "Deploy"

- [ ] Streamlit Cloud account created
- [ ] App deployment started
- [ ] Build completed successfully

### Step 5: Verify Deployment
- [ ] Dashboard loads at Streamlit URL
- [ ] All sections display correctly
- [ ] Charts render properly
- [ ] Parameter controls work
- [ ] Data displays correctly
- [ ] No errors in console

---

## Post-Deployment

### Share Your Dashboard
- [ ] Copy your Streamlit URL
- [ ] Test URL in different browsers
- [ ] Share with team/stakeholders

Your URL will be:
```
https://YOUR-APP-NAME.streamlit.app
```

### Monitor Your App
- [ ] Check analytics on Streamlit Cloud
- [ ] Review logs for errors
- [ ] Monitor performance

### Update Your Dashboard
When you make changes:
```bash
git add .
git commit -m "Description of changes"
git push
```
- [ ] Changes pushed to GitHub
- [ ] Streamlit auto-redeployed
- [ ] Updates verified

---

## Troubleshooting

### If deployment fails:

#### "Module not found" error
- [ ] Check `requirements.txt` has all dependencies
- [ ] Verify package names are correct
- [ ] Check Python version compatibility

#### "File not found" error
- [ ] Verify all data files are in repository
- [ ] Check file paths in code
- [ ] Ensure `outputs/` folder is committed

#### Git push fails
- [ ] Use Personal Access Token (not password)
- [ ] Check repository URL is correct
- [ ] Verify you have write access

#### App won't start
- [ ] Check logs in Streamlit Cloud
- [ ] Test locally first
- [ ] Verify `working_dashboard.py` is correct file

---

## Quick Commands Reference

```bash
# Check git status
git status

# Add all changes
git add .

# Commit with message
git commit -m "Your message here"

# Push to GitHub
git push

# View commit history
git log --oneline

# Check remote URL
git remote -v

# Pull latest changes
git pull
```

---

## Support Resources

- **Streamlit Docs:** https://docs.streamlit.io/
- **Streamlit Forum:** https://discuss.streamlit.io/
- **GitHub Docs:** https://docs.github.com/
- **Git Tutorial:** https://git-scm.com/docs/gittutorial

---

## Success! 🎉

Once all items are checked, your dashboard is successfully deployed!

**Dashboard URL:** ___________________________

**Deployed on:** ___________________________

**Notes:** 
_______________________________________________
_______________________________________________
_______________________________________________
