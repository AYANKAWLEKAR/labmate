import NextAuth from "next-auth";
import { authOptions } from "./auth";

// Server-side auth helper for use in Server Components and API routes
export const { auth, signIn, signOut } = NextAuth(authOptions);

