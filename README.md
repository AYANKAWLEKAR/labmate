# Labmate MVP

A student-facing research matchmaking platform that connects students with research opportunities at top institutions. This MVP includes a FastAPI backend for resume parsing, web scraping, matching, and email generation, plus a Next.js frontend with authentication.

## Project Structure

```
labmate/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # FastAPI app with /match and /generate_email endpoints
│   │   └── services/
│   │       ├── resume_parser.py    # PDF parsing with PyMuPDF + spaCy
│   │       ├── scraper.py          # Web scraping with BeautifulSoup/Selenium
│   │       ├── matching.py          # BERTScore-based semantic matching
│   │       └── email_generator.py  # OpenAI cold email generation
│   └── requirements.txt
├── web/                  # Next.js frontend
│   ├── app/
│   │   ├── page.tsx              # Main matching interface
│   │   ├── auth/signin/          # Sign-in page
│   │   └── api/auth/[...nextauth]/ # Auth.js API routes
│   ├── lib/
│   │   ├── auth.ts      # NextAuth configuration
│   │   └── prisma.ts    # Prisma client
│   └── prisma/
│       └── schema.prisma # Prisma schema (you'll configure this)
└── README.md
```

## Features

- **Resume Parsing**: Extracts skills, interests, and experiences from PDF resumes using PyMuPDF and spaCy
- **Web Scraping**: Scrapes faculty pages from 6 NJ institutions (Rutgers, NJIT, Princeton, Stevens, TCNJ, Seton Hall) using BeautifulSoup and Selenium
- **Semantic Matching**: Uses BERTScore to compute similarity between resume and professor profiles, returns top 3 matches
- **Cold Email Generation**: Generates personalized outreach emails using OpenAI's GPT-4o-mini
- **Authentication**: NextAuth.js with Prisma adapter, supports GitHub OAuth and email/password
- **Session Management**: Tracks contacted professors to avoid repeat suggestions

## Backend Setup

### Prerequisites
- Python 3.9+
- Chrome/Chromium (for Selenium scraping)

### Installation

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Environment Variables

Create a `.env` file in `backend/`:

```env
OPENAI_API_KEY=your-openai-api-key
CORS_ORIGINS=http://localhost:3000
DATABASE_URL=postgresql://user:password@localhost:5432/labmate  # Optional for future Prisma integration
```

### Run Backend

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Check `http://localhost:8000/health` to verify.

## Frontend Setup

### Prerequisites
- Node.js 18+
- PostgreSQL database (for Prisma)

### Installation

```bash
cd web

# Install dependencies
npm install

# Configure Prisma (you'll set up the database connection)
# Edit prisma/schema.prisma and set your DATABASE_URL
```

### Environment Variables

Create a `.env.local` file in `web/`:

```env
# Database
DATABASE_URL="postgresql://user:password@localhost:5432/labmate"

# NextAuth
NEXTAUTH_SECRET="generate-a-random-secret-here"
NEXTAUTH_URL="http://localhost:3000"

# GitHub OAuth (optional)
GITHUB_CLIENT_ID="your-github-client-id"
GITHUB_CLIENT_SECRET="your-github-client-secret"

# Backend API
NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
```

### Database Setup

```bash
# Generate Prisma Client
npx prisma generate

# Run migrations
npx prisma migrate dev

# (Optional) Open Prisma Studio to view data
npx prisma studio
```

### Run Frontend

```bash
npm run dev
```

The app will be available at `http://localhost:3000`.

## Usage

1. **Sign In**: Use GitHub OAuth or create an account with email/password
2. **Upload Resume**: Upload a PDF resume
3. **Select Institutions**: Choose one or more NJ institutions
4. **Get Matches**: Click "Find my top 3 professors" to get ranked matches
5. **Select Professor**: Click on a professor card to select them
6. **Generate Email**: Enter your name and click "Generate cold email"

## Web Scraping Details

The scraper (`backend/app/services/scraper.py`) supports both BeautifulSoup (for static HTML) and Selenium (for JavaScript-rendered content). Each institution has a configuration with:

- Base URL for faculty pages
- CSS selectors for professor containers, names, departments, research focus, and profile links
- Fallback patterns if primary selectors fail

**Note**: Real-world scraping will require institution-specific adjustments as website structures vary. The current implementation provides a solid foundation that can be extended with LangGraph-based orchestration.

## Matching Algorithm

The matching pipeline:
1. Converts resume profile (skills, interests, experiences) into a text representation
2. Converts each professor profile into a text representation
3. Uses BERTScore to compute semantic similarity (F1 score)
4. Ranks professors by similarity and returns top 3

BERTScore will download models on first run (~400MB).

## API Endpoints

### `POST /match`
- **Body**: Form data with `resume` (PDF file) and `institutions` (query params)
- **Response**: `{ resume_profile: {...}, top_professors: [...] }`

### `POST /generate_email`
- **Body**: `{ resume_profile: {...}, professor: {...}, user_name: string }`
- **Response**: `{ email_text: string }`

### `GET /health`
- **Response**: `{ status: "healthy" }`

## Next Steps

- [ ] Connect Prisma to backend for professor caching
- [ ] Implement LangGraph-based scraping orchestration
- [ ] Add professor exclusion logic (prevent showing already-contacted professors)
- [ ] Enhance resume parsing with more sophisticated NLP
- [ ] Add email tracking and analytics
- [ ] Deploy backend and frontend

## License

MIT