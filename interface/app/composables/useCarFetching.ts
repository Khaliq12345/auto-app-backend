import type { CarData, CarsResponse, CarsResponseDetails } from "~/types";

export function useCarFetching() {
  // Configuration
  const DEFAULT_LIMIT = 20;
  const MAX_RETRIES = 3;
  const RETRY_DELAY = 2000;

  // Reactive state
  const cars = ref<CarData[]>([]);
  const isLoading = ref(false);
  const fetchError = ref<string | null>(null);
  const hasMounted = ref(false);
  const total = ref(0);

  // Determine active domain from route for filtering cars by source platform
  const activeDomain = computed(() => {
    const route = useRoute();
    if (route.path === "/home" || route.path === "/") {
      return null;
    }
    if (
      typeof route.params.domain === "string" &&
      route.params.domain !== "home"
    ) {
      return route.params.domain;
    }
    const segments = route.path.split("/").filter(Boolean);
    return segments.length > 0 && segments[0] !== "home" ? segments[0] : null;
  });

  // Methods
  async function fetchCars() {
    isLoading.value = true;
    fetchError.value = null;
    cars.value = [];

    const limit = DEFAULT_LIMIT;
    let offset = 0;
    let consecutiveErrors = 0;

    try {
      while (true) {
        try {
          const response = await $fetch<CarsResponse>("/api/cars", {
            query: {
              offset,
              limit,
              cut_off_price: 500,
              percentage_limit: 95,
              domain: activeDomain.value ?? undefined,
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

          if (responseDetails.length < limit) {
            break;
          }

          offset += limit;
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

  // Watchers
  watch(
    () => activeDomain.value,
    async () => {
      if (!hasMounted.value) return;
      await fetchCars();
    },
  );

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
  };
}
