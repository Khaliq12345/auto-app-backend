<template>
    <div class="space-y-6">
        <!-- Filter Section -->
        <UCard class="p-6">
            <template #header>
                <h2 class="text-xl font-semibold">Filters</h2>
            </template>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                <UFormField label="Cut Off Price">
                    <UInput
                        v-model="filters.cutOffPrice"
                        type="number"
                        placeholder="Enter price"
                        icon="i-heroicons-currency-euro"
                    />
                </UFormField>
                <UFormField label="Matching Percent">
                    <UInput
                        v-model="filters.matchingPercent"
                        type="number"
                        placeholder="Enter percentage"
                        icon="i-heroicons-chart-bar"
                        min="0"
                        max="100"
                    />
                </UFormField>
                <UFormField label="Name">
                    <UInput
                        v-model="filters.name"
                        placeholder="Enter car name"
                        icon="i-heroicons-magnifying-glass"
                    />
                </UFormField>
                <UFormField label="Model">
                    <UInput
                        v-model="filters.model"
                        placeholder="Enter model"
                        icon="i-heroicons-tag"
                    />
                </UFormField>
                <UFormField label="Deals">
                    <USelect
                        v-model="filters.deals"
                        :items="dealOptions"
                        placeholder="Select deal option"
                        icon="i-heroicons-star"
                    />
                </UFormField>
            </div>
            <template #footer>
                <div class="flex justify-end gap-2">
                    <UButton variant="outline" @click="resetFilters">
                        Reset
                    </UButton>
                </div>
            </template>
        </UCard>

        <!-- Cars Section -->
        <div class="space-y-4">
            <div class="flex justify-between items-center">
                <h2 class="text-xl font-semibold">
                    Cars ({{ filteredCars.length }})
                </h2>
            </div>
            <UAlert
                v-if="fetchError"
                color="error"
                variant="soft"
                icon="i-heroicons-exclamation-triangle"
            >
                {{ fetchError }}
            </UAlert>
            <UAlert
                v-else-if="isLoading"
                color="info"
                variant="soft"
                icon="i-heroicons-arrow-path"
            >
                Chargement des voitures... ({{ cars.length }} chargées)
            </UAlert>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <UCard
                    v-for="car in paginatedCars"
                    :key="car.id"
                    class="overflow-hidden"
                    :class="getCardColorClass(car.card_color)"
                >
                    <div class="space-y-4">
                        <!-- Car Header -->
                        <div class="flex justify-between items-start">
                            <div>
                                <h3 class="font-semibold text-lg">
                                    {{ car.make }}
                                </h3>
                                <p class="text-sm text-gray-600">
                                    {{ car.model }}
                                </p>
                                <p class="text-xs text-gray-500">
                                    {{ car.version }}
                                </p>
                            </div>
                            <UBadge
                                :color="getDealBadgeColor(car.card_color)"
                                variant="soft"
                            >
                                {{ car.card_color }}
                            </UBadge>
                        </div>
                        <!-- Car Details -->
                        <div class="grid grid-cols-2 gap-3 text-sm">
                            <div>
                                <span class="text-gray-600">Color:</span>
                                <p class="font-medium">{{ car.color }}</p>
                            </div>
                            <div>
                                <span class="text-gray-600">Mileage:</span>
                                <p class="font-medium">
                                    {{ car.mileage?.toLocaleString() }} km
                                </p>
                            </div>
                            <div>
                                <span class="text-gray-600">Fuel:</span>
                                <p class="font-medium">{{ car.fuel_type }}</p>
                            </div>
                            <div>
                                <span class="text-gray-600">Year:</span>
                                <p class="font-medium">
                                    {{ car.year_from }}-{{ car.year_to }}
                                </p>
                            </div>
                        </div>
                        <!-- Price Information -->
                        <div class="border-t pt-3">
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-sm text-gray-600"
                                    >Price with tax:</span
                                >
                                <span class="font-bold text-lg"
                                    >€{{
                                        car.price_with_tax?.toLocaleString()
                                    }}</span
                                >
                            </div>
                            <div class="flex justify-between items-center">
                                <span class="text-sm text-gray-600"
                                    >Price without tax:</span
                                >
                                <span class="font-medium"
                                    >€{{
                                        car.price_with_no_tax?.toLocaleString()
                                    }}</span
                                >
                            </div>
                        </div>
                        <!-- Match Information -->
                        <div
                            v-if="car.best_match_percentage > 0"
                            class="bg-gray-50 p-3 rounded-lg"
                        >
                            <div class="flex justify-between items-center">
                                <span class="text-sm text-gray-600"
                                    >Best Match:</span
                                >
                                <span class="font-medium"
                                    >{{ car.best_match_percentage }}%</span
                                >
                            </div>
                        </div>
                        <!-- Actions -->
                        <div class="flex gap-2 pt-2">
                            <UButton
                                :to="car.car_url"
                                target="_blank"
                                variant="outline"
                                size="sm"
                                icon="i-heroicons-arrow-top-right-on-square"
                                class="flex-1"
                            >
                                View Car
                            </UButton>
                            <UButton
                                v-if="
                                    car.comparisons &&
                                    car.comparisons.length > 0
                                "
                                @click="openComparison(car)"
                                size="sm"
                                icon="i-heroicons-chart-bar-square"
                                class="flex-1"
                            >
                                Compare
                            </UButton>
                        </div>
                        <!-- Updated Date -->
                        <div class="text-xs text-gray-500 text-center">
                            Updated:
                            {{ new Date(car.updated_at).toLocaleDateString() }}
                        </div>
                    </div>
                </UCard>
            </div>
        </div>
        <!-- Pagination -->
        <div v-if="filteredCars.length > 0" class="flex justify-center mt-6">
            <UPagination
                v-model:page="currentPage"
                :total="filteredCars.length"
                :items-per-page="ITEMS_PER_PAGE"
                :show-controls="true"
                :sibling-count="1"
                show-edges
            />
        </div>
        <!-- Comparison Modal -->
        <UModal v-model:open="isComparisonOpen" title="Car Comparisons">
            <template #body>
                <ComparisonCards
                    v-if="selectedCar"
                    :comparisons="selectedCar.comparisons"
                    :slug="`${selectedCar.make} ${selectedCar.model}`"
                />
            </template>
        </UModal>
    </div>
</template>

<script setup lang="ts">
import type { CarData, Filters, CarsResponse, CarsResponseDetails } from "~/types";

// Configuration
const DEFAULT_LIMIT = 20;
const ITEMS_PER_PAGE = 20;
const DEFAULT_CUT_OFF_PRICE = 500;
const DEFAULT_PERCENTAGE_LIMIT = 95;
const MAX_RETRIES = 3;
const RETRY_DELAY = 2000; // 2 secondes entre les retries

const route = useRoute();
const cars = ref<CarData[]>([]);
const isLoading = ref(false);
const fetchError = ref<string | null>(null);
const hasMounted = ref(false);
const currentPage = ref(1);
const total = ref(0);

const activeDomain = computed(() => {
    if (route.path === "/home" || route.path === "/") {
        return null;
    }
    if (typeof route.params.domain === "string" && route.params.domain !== "home") {
        return route.params.domain;
    }
    const segments = route.path.split("/").filter(Boolean);
    return segments.length > 0 && segments[0] !== "home" ? segments[0] : null;
});

const filters = ref<Filters>({
    cutOffPrice: null,
    matchingPercent: null,
    name: "",
    model: "",
    deals: "",
});

const queryParams = computed(() => ({
    cut_off_price:
        filters.value.cutOffPrice ?? DEFAULT_CUT_OFF_PRICE,
    percentage_limit:
        filters.value.matchingPercent ?? DEFAULT_PERCENTAGE_LIMIT,
}));

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
                        cut_off_price: queryParams.value.cut_off_price,
                        percentage_limit: queryParams.value.percentage_limit,
                        domain: activeDomain.value ?? undefined,
                    },
                });

                consecutiveErrors = 0; // Reset consecutive errors on success

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
                
                console.error('Request error:', {
                    offset,
                    status: batchError.status,
                    statusCode: batchError.statusCode,
                    statusMessage: batchError.statusMessage,
                    message: batchError.message,
                });
                
                // Si on a trop d'erreurs consécutives
                if (consecutiveErrors >= MAX_RETRIES) {
                    // Si on a déjà des données, c'est un succès partiel
                    if (cars.value.length > 0) {
                        fetchError.value = `Chargement partiel : ${cars.value.length} voitures chargées. Impossible de charger plus de données à partir de l'offset ${offset}.`;
                        break;
                    } else {
                        throw batchError;
                    }
                }
                
                // Retry avec délai
                await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
            }
        }
        
        total.value = cars.value.length;
        
    } catch (error: any) {
        fetchError.value =
            error?.statusMessage || error?.message || "Échec du chargement des voitures";
        
        if (cars.value.length === 0) {
            cars.value = [];
            total.value = 0;
        }
    } finally {
        isLoading.value = false;
    }
}

onMounted(async () => {
    await fetchCars();
    hasMounted.value = true;
});

watch(
    () => [
        queryParams.value.cut_off_price,
        queryParams.value.percentage_limit,
        activeDomain.value,
    ],
    async () => {
        if (!hasMounted.value) return;
        await fetchCars();
    },
);

watch(currentPage, () => {
    // No fetch, just update display
});

const dealOptions = [
    { label: "Best Deals", value: "Best Deals" },
    { label: "Worst Deals", value: "Worst Deals" },
    { label: "Not Bad", value: "Not Bad" },
];

const isComparisonOpen = ref(false);
const selectedCar = ref<CarData | null>(null);

const filteredCars = computed(() => {
    let result = [...cars.value];
    if (filters.value.name) {
        result = result.filter((car) =>
            car.make.toLowerCase().includes(filters.value.name.toLowerCase()),
        );
    }
    if (filters.value.model) {
        result = result.filter((car) =>
            car.model.toLowerCase().includes(filters.value.model.toLowerCase()),
        );
    }
    if (filters.value.deals) {
        result = result.filter((car) => {
            const dealType = filters.value.deals;
            if (dealType === "Best Deals") return car.card_color === "green";
            if (dealType === "Worst Deals") return car.card_color === "red";
            if (dealType === "Not Bad") return car.card_color === "yellow";
            return true;
        });
    }
    return result;
});

const paginatedCars = computed(() => {
    const start = (currentPage.value - 1) * ITEMS_PER_PAGE;
    const end = start + ITEMS_PER_PAGE;
    return filteredCars.value.slice(start, end);
});

function resetFilters() {
    filters.value = {
        cutOffPrice: null,
        matchingPercent: null,
        name: "",
        model: "",
        deals: "",
    };
}

function openComparison(car: CarData) {
    selectedCar.value = car;
    isComparisonOpen.value = true;
}

function getCardColorClass(color: string) {
    switch (color) {
        case "red":
            return "border-l-4 border-red-500";
        case "green":
            return "border-l-4 border-green-500";
        case "yellow":
            return "border-l-4 border-yellow-500";
        default:
            return "border-l-4 border-gray-300";
    }
}

function getDealBadgeColor(
    cardColor: string,
): "success" | "error" | "warning" | "neutral" {
    switch (cardColor) {
        case "green":
            return "success";
        case "red":
            return "error";
        case "yellow":
            return "warning";
        default:
            return "neutral";
    }
}
</script>