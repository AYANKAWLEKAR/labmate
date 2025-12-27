# Google OAuth Setup Guide

This guide will help you set up Google OAuth authentication for Labmate.

## Step 1: Create Google OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services** > **Credentials**
4. Click **Create Credentials** > **OAuth client ID**
5. If prompted, configure the OAuth consent screen:
   - Choose **External** (unless you have a Google Workspace)
   - Fill in the required information:
     - App name: "Labmate"
     - User support email: Your email
     - Developer contact: Your email
   - Add scopes: `email`, `profile`, `openid`
   - Add test users (for development)
6. Create OAuth client ID:
   - Application type: **Web application**
   - Name: "Labmate Web Client"
   - Authorized JavaScript origins:
     - `http://localhost:3000` (for development)
     - `https://yourdomain.com` (for production)
   - Authorized redirect URIs:
     - `http://localhost:3000/api/auth/callback/google` (for development)
     - `https://yourdomain.com/api/auth/callback/google` (for production)
7. Click **Create**
8. Copy the **Client ID** and **Client Secret**

## Step 2: Add Environment Variables

Add the following to your `web/.env.local` file:

```env
GOOGLE_CLIENT_ID="your-google-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-google-client-secret"
```

## Step 3: How It Works

When a user clicks "Continue with Google":

1. **User clicks button** → Redirected to Google OAuth consent screen
2. **User authorizes** → Google redirects back to `/api/auth/callback/google`
3. **NextAuth processes callback** → The Prisma adapter automatically:
   - Creates a new `User` record (if email doesn't exist)
   - Creates/updates an `Account` record linking Google account to user
   - Creates a `Session` record for the authenticated session
4. **User redirected** → Back to home page (`/`) as authenticated user

## Database Records Created

The Prisma adapter automatically manages:

- **User table**: Creates user with email, name, and image from Google profile
- **Account table**: Links Google OAuth account to the user
- **Session table**: Creates active session for the user

## Testing

1. Start your development server: `npm run dev`
2. Navigate to `http://localhost:3000/auth/signin`
3. Click "Continue with Google"
4. Sign in with your Google account
5. You should be redirected to the home page

## Troubleshooting

### "redirect_uri_mismatch" Error
- Make sure the redirect URI in Google Console exactly matches: `http://localhost:3000/api/auth/callback/google`
- Check for trailing slashes or protocol mismatches (http vs https)

### "access_denied" Error
- Make sure you've added your email as a test user in the OAuth consent screen (for development)
- Check that the OAuth consent screen is published (for production)

### User Not Created in Database
- Verify `DATABASE_URL` is correct in `.env.local`
- Check that Prisma migrations have been run: `npx prisma migrate dev`
- Check server logs for any Prisma errors

## Production Setup

For production:

1. Update OAuth consent screen to **Published** status
2. Add production domain to authorized origins and redirect URIs
3. Update `NEXTAUTH_URL` environment variable to your production URL
4. Ensure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set in production environment

