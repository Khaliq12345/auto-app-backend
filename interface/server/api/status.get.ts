export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();
  const query = getQuery(event) as Record<string, any>;
  
  const backendUrl = config.public.backendUrl || 'http://127.0.0.1:5000';
  const apiUrl = `${backendUrl}/scrape_status`;

  // Vérifier que les tokens d'authentification sont présents
  if (!query.access_token || !query.refresh_token) {
    throw createError({
      statusCode: 400,
      statusMessage: "Missing required authentication tokens (access_token, refresh_token)",
    });
  }

  try {
    const response = await $fetch(apiUrl, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      query: {
        access_token: query.access_token,
        refresh_token: query.refresh_token,
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
