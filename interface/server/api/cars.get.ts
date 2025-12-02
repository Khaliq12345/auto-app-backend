export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();
  const query = getQuery(event) as Record<string, any>;

  const backendUrl = config.backendUrl;
  const apiUrl = `${backendUrl}/get_all_cars`;

  try {
    const response = await $fetch(apiUrl, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      query: query,
      // IMPORTANT: Augmenter le timeout à 2 minutes
      timeout: 120000, // 120 secondes = 2 minutes

      // Désactiver la validation du statut pour gérer nous-mêmes
      onResponseError({ response }) {
        // Error handled in catch block
      },

      onRequestError({ error }) {
        // Error handled in catch block
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
        statusMessage: "Cars not found",
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
        statusMessage: `Backend server error: ${error.data?.detail || error.message}`,
      });
    }

    // Erreur de timeout
    if (error.message?.includes("timeout") || error.code === "ETIMEDOUT") {
      throw createError({
        statusCode: 504,
        statusMessage: "Request timeout - backend took too long to respond",
      });
    }

    // Erreur générale
    throw createError({
      statusCode: 500,
      statusMessage: `Internal server error: ${error.message}`,
    });
  }
});
