import { writeFile, mkdir } from "fs/promises";
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

  // Nom du fichier
  const name = "25630.xlsx";

  // 🔥 Emplacement : auto-app-backend/files/uploads
  const uploadDir = path.join(process.cwd(), "..", "files", "uploads");

  // Crée le dossier si nécessaire (évite ENOENT)
  await mkdir(uploadDir, { recursive: true });

  const filePath = path.join(uploadDir, name);

  // Sauvegarde du fichier
  await writeFile(filePath, file.data);

  return {
    success: true,
    saved: filePath,
  };
});
