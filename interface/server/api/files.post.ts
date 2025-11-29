import { writeFile } from "fs/promises";
import path from "path";
import { defineEventHandler, readMultipartFormData } from "h3";

export default defineEventHandler(async (event) => {
  const form = await readMultipartFormData(event);
  if (!form) {
    throw createError({ statusCode: 400, message: "No file uploaded" });
  }

  const file = form.find((f) => f.name === "file");
  if (!file) {
    throw createError({ statusCode: 400, message: "Missing file" });
  }
  const name = "25630.xlsx";
  // Sauvegarde dans /public/uploads/
  const uploadDir = path.join(process.cwd(), "public", "uploads");
  const filePath = path.join(uploadDir, name || "uploaded.xlsx");

  await writeFile(filePath, file.data);

  return {
    success: true,
    url: `/uploads/${name}`,
  };
});
