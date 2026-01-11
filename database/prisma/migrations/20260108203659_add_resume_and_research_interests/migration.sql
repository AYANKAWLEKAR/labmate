-- AlterTable
ALTER TABLE "User" ADD COLUMN     "researchInterests" TEXT[];

-- CreateTable
CREATE TABLE "resumes" (
    "id" TEXT NOT NULL,
    "rawpdf" TEXT,
    "skills" TEXT[],
    "experiences" JSONB,
    "userId" TEXT NOT NULL,

    CONSTRAINT "resumes_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "resumes_userId_key" ON "resumes"("userId");

-- AddForeignKey
ALTER TABLE "resumes" ADD CONSTRAINT "resumes_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
