import { defineEventHandler, readBody, createError } from "h3";

interface StartScraperRequest {
  mileage_plus_minus?: number | null;
  ignore_old?: boolean | null;
  sites_to_scrape: string[];
  dev?: boolean | null;
  car_id?: number | string | null;
}

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();

  const body = await readBody<StartScraperRequest>(event);

  if (!body.sites_to_scrape || body.sites_to_scrape.length === 0) {
    throw createError({
      statusCode: 400,
      message: "sites_to_scrape is required",
    });
  }

  const backendURL = `${config.backendUrl}/start-task`;

  // Préparer le payload en envoyant null pour les valeurs non définies
  // Le backend gère les valeurs par défaut
  const payload = {
    mileage_plus_minus: body.mileage_plus_minus ?? null,
    ignore_old: body.ignore_old ?? null,
    sites_to_scrape: body.sites_to_scrape,
    dev: body.dev ?? null,
    car_id: body.car_id ?? null,
  };

  try {
    const response = await $fetch(backendURL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: payload,
    });

    return {
      success: true,
      data: response,
    };
  } catch (err: any) {
    return {
      success: false,
      error: err?.data || err?.message || err,
    };
  }
});
