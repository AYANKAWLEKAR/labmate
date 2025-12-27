import NextAuth from "next-auth";
import { authOptions } from "@/lib/auth";
import { NextResponse } from "next/server";

const handler = NextAuth(authOptions);

export async function GET(request: Request) {
  try {
    return await handler(request);
  } catch (error) {
    console.error("NextAuth GET error:", error);
    // Return JSON error instead of HTML error page
    return NextResponse.json(
      { 
        error: "Authentication service error",
        message: error instanceof Error ? error.message : "Unknown error"
      },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    return await handler(request);
  } catch (error) {
    console.error("NextAuth POST error:", error);
    // Return JSON error instead of HTML error page
    return NextResponse.json(
      { 
        error: "Authentication service error",
        message: error instanceof Error ? error.message : "Unknown error"
      },
      { status: 500 }
    );
  }
}

