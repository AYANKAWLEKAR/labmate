import NextAuth from "next-auth";
import { authOptions } from "@/lib/auth";

// Initialize NextAuth and get handlers
const nextAuth = NextAuth(authOptions);

// Export handlers for GET and POST requests
export { nextAuth as GET, nextAuth as POST };