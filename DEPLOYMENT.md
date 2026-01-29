# 🚀 Streamlit Cloud Deployment Guide

## Pre-Deployment Checklist ✅

Run this command to verify readiness:
```bash
python check_deployment.py
```

---

## Step-by-Step Deployment

### 1. GitHub Setup

```bash
# Make sure all changes are committed
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### 2. Streamlit Cloud Configuration

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repository: `civinigrani`
5. Set branch: `main` (or your default branch)
6. Set main file path: `Home.py`
7. Click **"Deploy!"**

### 3. Configure Secrets

After deployment starts:

1. Click on **"⚙️ Settings"** in your app dashboard
2. Go to **"Secrets"** tab  
3. Paste the following (replace with your actual keys):

```toml
# Optional: NewsAPI for live news analysis
NEWS_API_KEY = "your_actual_key_from_newsapi.org"
```

4. Click **"Save"**

### 4. Monitor Deployment

- Watch the **build logs** for any errors
- First deployment takes ~5-10 minutes
- Subsequent deploys are faster (cached dependencies)

---

## Troubleshooting

### Issue: Memory Error During Prophet Training

**Solution**: Prophet models cache in `data/cache/`. Pre-train models locally and commit them:
```bash
# Run app locally first to generate cached models
streamlit run Home.py
# Then commit the cache
git add data/cache
git commit -m "Add pre-trained Prophet models"
git push
```

### Issue: GeoPandas Import Error

**Solution**: The `packages.txt` file should handle this. If it fails, try upgrading:
```toml
# In requirements.txt
geopandas>=0.14.0
```

### Issue: App is Slow

**Solutions**:
1. Enable caching aggressively (already done with `@st.cache_data`)
2. Reduce forecast lookback period
3. Consider upgrading to Streamlit Cloud paid tier

---

## Custom Domain (Optional)

1. Go to app settings
2. Click "Custom domain"
3. Add your domain (e.g., `civinigrani.yourdomain.com`)
4. Follow DNS configuration instructions

---

## Auto-Deployment

Every `git push` to your main branch will trigger automatic redeployment! 🎉

---

## Monitoring

- **App URL**: `https://[your-app-name].streamlit.app`
- **Analytics**: Available in Streamlit Cloud dashboard
- **Logs**: Click "Manage app" → "Logs"

---

## Data Updates

To update PDS/PGSM data:

1. Update CSVs in `data/raw/`
2. Commit and push
3. Auto-redeploys with fresh data

Or use scripts:
```bash
python scripts/scrape_data.py
git add data/
git commit -m "Update data"
git push
```

---

## Cost

**Free Tier** includes:
- 1 GB RAM
- 1 CPU core
- Unlimited public apps
- Community support

**Paid Tiers** ($20/month+):
- More resources
- Private apps
- Priority support
- Custom domains

---

## Security Notes

✅ **Secrets are encrypted** on Streamlit Cloud  
✅ **Never commit** `.streamlit/secrets.toml` to git  
✅ **Use secrets** for all API keys  
✅ **Review** `.gitignore` before pushing

---

## Support

- **Streamlit Docs**: https://docs.streamlit.io/streamlit-community-cloud
- **Community Forum**: https://discuss.streamlit.io
- **GitHub Issues**: Create issue in your repo

---

**Your app is now live! Share the URL with the world! 🌍**
