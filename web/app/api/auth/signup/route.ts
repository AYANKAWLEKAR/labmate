//sign up with just email and password

import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { hash } from "bcryptjs";
//import { NextAuthOptions } from "next-auth";
import { PrismaAdapter } from "@auth/prisma-adapter";


//request is a post request because new user is being created
// new session and new account

export async function POST(request: NextRequest) {

    try{ 
        const body=await request.json();
        const email=body.email;
        const password=body.password;
        
        //const name=body.name;
       

        if (!email || !password ) {

            return NextResponse.json({ error: "Missing username or password " }, { status: 400 });

        }
        const existingUser=await prisma.user.findUnique({
            where: { email },
        });
        if (existingUser) {
            return NextResponse.json({ error: "User already exists" }, { status: 400 });
        }
        else{

            const hashedPassword=await hash(password, 10);
            const user=await prisma.user.create({
                data: { email: email, hashedPassword: hashedPassword, name:email, emailsSent:0, contactedProfessors:[] },
            });
            return NextResponse.json({message:"User Created with return + ${user.id}", userId: user.id, userEmail:user.email}, { status: 201 });
        }

    } catch (error) {
        console.error(error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
    
}
