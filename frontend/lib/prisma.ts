import { PrismaClient } from "../../database/generated/prisma/client";
// Importing from database folder node_modules
import { PrismaPg } from "../../database/node_modules/@prisma/adapter-pg";
// @ts-expect-error - TypeScript doesn't resolve types from external node_modules path
import { Pool } from "../../database/node_modules/pg";

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

const adapter = new PrismaPg(pool);

export const prisma: PrismaClient =
  globalForPrisma.prisma ??
  new PrismaClient({
    adapter,
  }) as PrismaClient;

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma;

