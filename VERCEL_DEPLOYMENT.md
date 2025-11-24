# Vercel Deployment Guide

This guide will help you deploy the Chatbot with Sentiment Analysis web application to Vercel.

## 📋 Prerequisites

1. A GitHub account
2. A Vercel account (sign up at [vercel.com](https://vercel.com))
3. Git installed on your local machine

## 🚀 Deployment Steps

### Step 1: Prepare Your Repository

1. **Ensure all files are committed:**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   ```

2. **Push to GitHub:**
   ```bash
   git push origin main
   ```
   (Replace `main` with your branch name if different)

### Step 2: Deploy to Vercel

#### Option A: Deploy via Vercel Dashboard (Recommended)

1. **Go to [vercel.com](https://vercel.com)** and sign in
2. **Click "Add New Project"**
3. **Import your GitHub repository:**
   - Select your repository from the list
   - Click "Import"
4. **Configure the project:**
   - **Framework Preset:** Other
   - **Root Directory:** `./` (leave as default)
   - **Build Command:** Leave empty (Vercel will auto-detect)
   - **Output Directory:** Leave empty
   - **Install Command:** `pip install -r requirements.txt`
5. **Click "Deploy"**
6. **Wait for deployment to complete** (usually 2-3 minutes)

#### Option B: Deploy via Vercel CLI

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy:**
   ```bash
   vercel
   ```

4. **Follow the prompts:**
   - Set up and deploy? **Yes**
   - Which scope? **Your account**
   - Link to existing project? **No**
   - Project name? **chatbot-sentiment** (or your choice)
   - Directory? **./**

5. **For production deployment:**
   ```bash
   vercel --prod
   ```

## 📁 Project Structure for Vercel

The project is configured with the following structure:

```
.
├── api/
│   └── index.py          # Vercel serverless function handler
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── style.css         # Styles
│   └── script.js         # Frontend JavaScript
├── src/                  # Source code modules
├── config/               # Configuration files
├── vercel.json           # Vercel configuration
├── .vercelignore        # Files to ignore during deployment
└── requirements.txt      # Python dependencies
```

## ⚙️ Configuration Files

### `vercel.json`
- Configures Vercel to use Python runtime
- Routes all requests to the Flask app
- Sets maximum function duration to 30 seconds

### `api/index.py`
- Vercel serverless function entry point
- Handles all routes (/, /api/chat, /api/end_conversation, /api/reset)
- Uses client-side session management (localStorage)

### `.vercelignore`
- Excludes unnecessary files from deployment
- Reduces deployment size and build time

## 🔧 Important Notes

### Session Management
- **Vercel doesn't support Flask sessions** (serverless functions are stateless)
- The app uses **client-side session management** with localStorage
- Session IDs are generated on the client and sent with each request

### File Storage
- **Conversation saving is disabled** on Vercel (read-only filesystem)
- In production, consider using:
  - Vercel KV (Redis)
  - Vercel Postgres
  - External database (MongoDB, PostgreSQL, etc.)

### Environment Variables
If you need to set environment variables:

1. **Via Dashboard:**
   - Go to Project Settings → Environment Variables
   - Add variables (e.g., `SECRET_KEY`)

2. **Via CLI:**
   ```bash
   vercel env add SECRET_KEY
   ```

## 🌐 Accessing Your Deployed App

After deployment, Vercel will provide:
- **Production URL:** `https://your-project-name.vercel.app`
- **Preview URLs:** For each deployment

## 🔄 Updating Your Deployment

### Automatic Updates
- **Vercel automatically deploys** when you push to your main branch
- Each push creates a new preview deployment
- Production deployment requires manual promotion or auto-deploy from main branch

### Manual Updates
```bash
git add .
git commit -m "Update application"
git push origin main
```

Vercel will automatically detect the push and redeploy.

## 🐛 Troubleshooting

### Build Fails
1. **Check Python version:** Ensure `requirements.txt` has compatible versions
2. **Check logs:** View build logs in Vercel dashboard
3. **Test locally:** Run `python api/index.py` to check for errors

### Runtime Errors
1. **Check function logs:** View runtime logs in Vercel dashboard
2. **Verify imports:** Ensure all modules are in `src/` directory
3. **Check paths:** Verify file paths are correct for Vercel's filesystem

### Static Files Not Loading
1. **Check `vercel.json` routes:** Ensure static files route is correct
2. **Verify file paths:** Use relative paths in HTML/CSS/JS
3. **Check file permissions:** Ensure files are readable

## 📊 Monitoring

- **Vercel Dashboard:** View deployments, logs, and analytics
- **Function Logs:** Real-time logs for debugging
- **Analytics:** Track usage and performance

## 🔒 Security Considerations

1. **Secret Key:** Use environment variables for sensitive data
2. **CORS:** Already configured for cross-origin requests
3. **Rate Limiting:** Consider adding rate limiting for production
4. **Input Validation:** Already implemented in the code

## 📝 Next Steps

1. **Set up custom domain** (optional)
2. **Configure environment variables** if needed
3. **Set up database** for conversation persistence
4. **Enable analytics** for usage tracking
5. **Configure CI/CD** for automated testing

## 🎉 Success!

Your chatbot is now live on Vercel! Share the URL with users and start collecting conversations.

---

**Need Help?**
- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Support](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [Flask on Vercel](https://vercel.com/guides/deploying-flask-with-vercel)

