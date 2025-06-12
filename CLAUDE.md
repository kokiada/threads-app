# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Threads automated posting application built with Google Apps Script. The application is a serverless solution for managing multiple Threads accounts and scheduling posts. It consists of a web-based dashboard interface and backend logic all running on Google's infrastructure.

**Key Project Structure:**
- Main application code is in `/gas-version/` directory
- Source code is in `/gas-version/src/` directory for clasp deployment
- Main logic: `Code.js` contains the entire backend and API integration
- Dashboard UI: `dashboard.html` contains the complete web interface
- CLI development support with clasp tool

## Development Commands

**Working Directory:** Always work from `/gas-version/` directory

```bash
# Google Apps Script authentication
npm run login

# Create new GAS project
npm run create

# Push code to Google Apps Script
npm run push

# Deploy as web app
npm run deploy

# Open GAS editor
npm run open

# Watch for changes and auto-push
npm run dev

# Push and deploy (production)
npm run prod
```

## Architecture Notes

**Platform Architecture:**
- Google Apps Script serverless platform
- HTML Service for web interface
- Google Spreadsheet as database
- Trigger-based scheduling system
- OAuth 2.0 for Threads API integration

**UI Framework:**
- Vanilla HTML5, CSS3, and JavaScript (ES6+)
- Responsive design with CSS Grid and Flexbox
- Modern gradient-based styling
- Mobile-first responsive design
- Modal-based interactions for all major functions

**Key Features Implemented:**
- Dashboard with account overview, scheduled posts, and recent posts
- Account management with encrypted token storage
- Post creation with support for TEXT, IMAGE, VIDEO types
- Scheduling system with automatic execution
- Comprehensive logging and error handling
- Google Drive integration for media files

**Data Structure:**
- Google Spreadsheet as database with sheets:
  - `accounts`: Account information and tokens
  - `scheduled_posts`: Pending scheduled posts
  - `post_history`: Completed post records
- Encrypted token storage for security
- JSON-based content serialization

## Development Notes

- Application uses Japanese language in the UI
- Mobile-optimized with touch-friendly interactions
- FAB (Floating Action Button) for quick post creation
- Supports immediate and scheduled posting with Threads API
- Account status tracking (active/expired tokens)
- Automatic retry mechanism for failed posts
- Comprehensive error logging with Google Apps Script Logger

## Google Apps Script Specific Notes

**Environment Variables:**
Set in Project Settings → Script Properties:
- `THREADS_CLIENT_ID`: Threads API client ID
- `THREADS_CLIENT_SECRET`: Threads API client secret
- `SPREADSHEET_ID`: Auto-created spreadsheet ID for data storage

**Triggers:**
- Time-based trigger: `processScheduledPosts()` runs every 5 minutes
- Manual setup via `setupTriggers()` function

**Security:**
- Token encryption using Base64 encoding
- Input validation and sanitization
- Rate limiting through GAS execution quotas
- Secure OAuth 2.0 flow implementation

## Deployment Methods

### Manual Deployment (GAS Editor)
1. Copy code to Google Apps Script editor
2. Set up environment variables
3. Deploy as web app

### CLI Deployment (Recommended)
1. Use clasp for local development
2. Push changes with `npm run push`
3. Deploy with `npm run deploy`

### Automated Deployment (CI/CD)
1. GitHub Actions workflow for automatic deployment
2. Push to `main` branch for production
3. Push to `develop` branch for development environment

## Testing

**Manual Testing:**
- Use `quickSetup()` function for initial setup with test data
- Test all functions through the web interface
- Monitor execution logs in GAS editor

**Integration Testing:**
- Test Threads API connectivity
- Verify spreadsheet operations
- Check trigger execution

## Important Notes

- All file changes should be made in `/gas-version/src/` directory
- Use `.js` extension for JavaScript files (not `.gs`)
- HTML files keep `.html` extension
- `appsscript.json` contains project configuration
- Never commit sensitive data or tokens to repository