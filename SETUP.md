# Labmate Setup Guide

## Quick Start

### 1. Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Set environment variables
export OPENAI_API_KEY="your-key-here"
export CORS_ORIGINS="http://localhost:3000"

# Run server
uvicorn app.main:app --reload --port 8000
```

**Note for Selenium**: If you plan to use Selenium scraping, install ChromeDriver:
- macOS: `brew install chromedriver`
- Linux: Download from https://chromedriver.chromium.org/
- Windows: Download and add to PATH

### 2. Frontend Setup

```bash
cd web
npm install

# Configure environment (create .env.local)
# DATABASE_URL="postgresql://..."
# NEXTAUTH_SECRET="..."
# NEXTAUTH_URL="http://localhost:3000"
# GITHUB_CLIENT_ID="..." (optional)
# GITHUB_CLIENT_SECRET="..." (optional)
# NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"

# Set up Prisma (you'll configure DATABASE_URL)
npx prisma generate
npx prisma migrate dev

# Run dev server
npm run dev
```

## Testing the Flow

1. Start backend: `uvicorn app.main:app --reload --port 8000`
2. Start frontend: `npm run dev` (in `web/` directory)
3. Open `http://localhost:3000`
4. Sign in (create account or use GitHub)
5. Upload a PDF resume
6. Select institutions
7. Click "Find my top 3 professors"
8. Select a professor
9. Enter your name and generate email

## Troubleshooting

### Backend Issues

- **spaCy model not found**: Run `python -m spacy download en_core_web_sm`
- **BERTScore slow first run**: It downloads models (~400MB) on first use
- **Scraping fails**: Websites may have changed structure; adjust selectors in `scraper.py`
- **OpenAI errors**: Check `OPENAI_API_KEY` is set correctly

### Frontend Issues

- **Prisma errors**: Make sure `DATABASE_URL` is correct and database exists
- **Auth not working**: Check `NEXTAUTH_SECRET` and `NEXTAUTH_URL` are set
- **API connection fails**: Verify `NEXT_PUBLIC_API_BASE_URL` matches backend URL

### Scraping Issues

- **BeautifulSoup fails**: Website may require JavaScript; switch to Selenium in config
- **Selenium fails**: Install ChromeDriver and ensure Chrome/Chromium is installed
- **Rate limiting**: Add delays between requests in `scraper.py`

## Next Steps

1. **Configure Prisma**: Set up your PostgreSQL database and update `DATABASE_URL`
2. **Customize Scraping**: Adjust selectors in `backend/app/services/scraper.py` for each institution
3. **Add LangGraph**: Replace simple scraping with LangGraph-based orchestration
4. **Enhance Matching**: Add exclusion logic for already-contacted professors
5. **Deploy**: Set up production deployments for both backend and frontend

