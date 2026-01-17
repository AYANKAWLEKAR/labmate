-- CreateTable
CREATE TABLE "departments" (
    "id" TEXT NOT NULL,
    "institution" TEXT NOT NULL,
    "departmentName" TEXT NOT NULL,
    "url" TEXT NOT NULL,
    "lastScrapedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "departments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "professors" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "institution" TEXT NOT NULL,
    "department" TEXT NOT NULL,
    "researchFocus" TEXT NOT NULL,
    "labGroup" TEXT,
    "profileUrl" TEXT,
    "departmentId" TEXT NOT NULL,

    CONSTRAINT "professors_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "departments_url_key" ON "departments"("url");

-- CreateIndex
CREATE UNIQUE INDEX "professors_name_departmentId_key" ON "professors"("name", "departmentId");

-- AddForeignKey
ALTER TABLE "professors" ADD CONSTRAINT "professors_departmentId_fkey" FOREIGN KEY ("departmentId") REFERENCES "departments"("id") ON DELETE CASCADE ON UPDATE CASCADE;
