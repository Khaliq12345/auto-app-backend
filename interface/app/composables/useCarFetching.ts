import type { CarData, CarsResponse, CarsResponseDetails } from "~/types";

interface UseCarFetchingOptions {
  domain?: string;
  limit?: number;
  cutOffPrice?: number | null | undefined;
  percentageLimit?: number | null | undefined;
}

export function useCarFetching(options: UseCarFetchingOptions = {}) {
  // Configuration
  const DEFAULT_LIMIT = 20;
  const DEFAULT_CUT_OFF_PRICE = 500;
  const DEFAULT_PERCENTAGE_LIMIT = 95;
  const MAX_RETRIES = 3;
  const RETRY_DELAY = 2000;

  const limit = ref(options.limit ?? DEFAULT_LIMIT);
  const cutOffPrice = ref<number | null | undefined>(
    options.cutOffPrice ?? DEFAULT_CUT_OFF_PRICE,
  );
  const percentageLimit = ref<number | null | undefined>(
    options.percentageLimit ?? DEFAULT_PERCENTAGE_LIMIT,
  );
  const domain = options.domain;

  // Reactive state
  const cars = ref<CarData[]>([]);
  const isLoading = ref(false);
  const fetchError = ref<string | null>(null);
  const hasMounted = ref(false);
  const total = ref(0);

  // Methods
  async function fetchCars() {
    isLoading.value = true;
    fetchError.value = null;
    cars.value = [];

    const currentLimit = limit.value ?? DEFAULT_LIMIT;
    let offset = 0;
    let consecutiveErrors = 0;

    try {
      while (true) {
        try {
          const response = await $fetch<CarsResponse>("/api/cars", {
            query: {
              offset,
              limit: currentLimit,
              cut_off_price: cutOffPrice.value ?? undefined,
              percentage_limit: percentageLimit.value ?? undefined,
              domain: domain ?? undefined,
            },
          });

          consecutiveErrors = 0;

          const detailsSource = Array.isArray(response.details)
            ? response.details
            : (response.details as CarsResponseDetails | undefined)?.data;

          const responseDetails = Array.isArray(detailsSource)
            ? detailsSource
            : [];

          if (!responseDetails.length) {
            break;
          }

          cars.value.push(...responseDetails);

          if (responseDetails.length < currentLimit) {
            break;
          }

          offset += currentLimit;
        } catch (batchError: any) {
          consecutiveErrors++;

          console.error("Request error:", {
            offset,
            status: batchError.status,
            statusCode: batchError.statusCode,
            statusMessage: batchError.statusMessage,
            message: batchError.message,
          });

          if (consecutiveErrors >= MAX_RETRIES) {
            if (cars.value.length > 0) {
              fetchError.value = `Chargement partiel : ${cars.value.length} voitures chargées. Impossible de charger plus de données à partir de l'offset ${offset}.`;
              break;
            } else {
              throw batchError;
            }
          }

          await new Promise((resolve) => setTimeout(resolve, RETRY_DELAY));
        }
      }

      total.value = cars.value.length;
    } catch (error: any) {
      fetchError.value =
        error?.statusMessage ||
        error?.message ||
        "Échec du chargement des voitures";

      if (cars.value.length === 0) {
        cars.value = [];
        total.value = 0;
      }
    } finally {
      isLoading.value = false;
    }
  }

  function setCutOffPrice(value: number | null | undefined) {
    cutOffPrice.value = value;
  }

  function setPercentageLimit(value: number | null | undefined) {
    percentageLimit.value = value;
  }

  function setLimit(value: number | null | undefined) {
    limit.value = value ?? DEFAULT_LIMIT;
  }

  // Lifecycle
  onMounted(async () => {
    await fetchCars();
    hasMounted.value = true;
  });

  return {
    cars,
    isLoading,
    fetchError,
    total,
    fetchCars,
    hasMounted,
    limit,
    cutOffPrice,
    percentageLimit,
    setCutOffPrice,
    setPercentageLimit,
    setLimit,
  };
}
