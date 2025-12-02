import { defineEventHandler, readMultipartFormData, createError } from "h3";

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();

  // Lire le multipart/form-data
  const form = await readMultipartFormData(event);

  if (!form || form.length === 0) {
    throw createError({ statusCode: 400, message: "No file uploaded" });
  }

  // Récupérer le fichier
  const file = form.find((f) => f.name === "file");

  if (!file) {
    throw createError({ statusCode: 400, message: "Missing file" });
  }

  // Récupérer le type d'upload
  const uploadTypeField = form.find((f) => f.name === "upload_type");
  const uploadType = uploadTypeField?.data?.toString() || "Input File";

  //  Nom original du fichier
  const filename = file.filename;

  const backendURL = `${config.backendUrl}/upload-file`;

  // Nitro fournit automatiquement FormData côté serveur
  const formData = new FormData();
  formData.append("file", new Blob([file.data]), filename);
  formData.append("upload_type", uploadType);

  try {
    const response = await $fetch(backendURL, {
      method: "POST",
      body: formData,
    });

    return {
      success: true,
      backend: response,
    };
  } catch (err: any) {
    return {
      success: false,
      error: err?.data || err?.message || err,
    };
  }
});
