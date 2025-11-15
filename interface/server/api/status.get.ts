export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();
  
  const backendUrl = config.public.backendUrl || 'http://127.0.0.1:5000';
  const apiUrl = `${backendUrl}/scrape_status`;

  try {
    const response = await $fetch(apiUrl, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    return response;
  } catch (error: any) {
    // Gestion des erreurs
    if (error.status === 401) {
      throw createError({
        statusCode: 401,
        statusMessage: "Invalid credentials",
      });
    }

    if (error.status === 404) {
      throw createError({
        statusCode: 404,
        statusMessage: "Scrape status not found",
      });
    }

    if (error.status >= 400 && error.status < 500) {
      throw createError({
        statusCode: error.status,
        statusMessage: String(error.data?.detail || "Bad request"),
      });
    }

    if (error.status >= 500) {
      throw createError({
        statusCode: 502,
        statusMessage: "Backend server error",
      });
    }

    // Erreur générale
    throw createError({
      statusCode: 500,
      statusMessage: "Internal server error",
    });
  }
});
