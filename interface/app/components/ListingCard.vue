<template>
    <div class="space-y-6">
        <!-- Filter Section -->
        <UCard class="p-6">
            <template #header>
                <h2 class="text-xl font-semibold">Filters</h2>
            </template>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                <UFormField label="Cut Off Price">
                    <div class="flex gap-2">
                        <UInput
                            v-model="filters.cutOffPrice"
                            type="number"
                            placeholder="Enter price"
                            icon="i-heroicons-currency-euro"
                        />
                        <UButton size="sm" @click="getCars()">Reload</UButton>
                    </div>
                </UFormField>
                <UFormField label="Matching Percent">
                    <div class="flex gap-2">
                        <UInput
                            v-model="filters.matchingPercent"
                            type="number"
                            placeholder="Enter percentage"
                            icon="i-heroicons-chart-bar"
                            min="0"
                            max="100"
                        />
                        <UButton size="sm" @click="getCars()">Reload</UButton>
                    </div>
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
                <div class="flex gap-4">
                    <UButton variant="outline" @click="resetFilters">
                        Reset
                    </UButton>
                    <UButton
                        @click="exportBestDealsHandler"
                        variant="solid"
                        color="success"
                        icon="i-heroicons-arrow-down-tray"
                        :disabled="cars.length === 0"
                    >
                        Export Best Deals
                    </UButton>
                    <UButton
                        @click="exportAllDealsHandler"
                        variant="solid"
                        color="primary"
                        icon="i-heroicons-arrow-down-tray"
                        :disabled="cars.length === 0"
                    >
                        Export All Deals
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

            <UBadge size="xl">Loading from Car - {{ cursor }} </UBadge>
            <UProgress animation="swing" v-if="isLoading"
                >Chargement des voitures...</UProgress
            >
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <CarCard
                    v-for="car in paginatedCars"
                    :key="car.id"
                    :car="car"
                    @compare="openComparison"
                />
            </div>
        </div>

        <!-- Pagination -->
        <div v-if="filteredCars.length > 0" class="flex justify-center mt-6">
            <UPagination
                v-model:page="currentPage"
                :total="filteredCars.length"
                :items-per-page="20"
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
import type { CarData, CarsResponse, CarsResponseDetails } from "~/types";

const props = defineProps<{
    domain: string | undefined;
}>();

const cars = ref([]);
const fetchError = ref();
const isLoading = ref(false);
const limit = ref(100);
const cursor = ref(undefined);

// Filters
const filters = ref({
    cutOffPrice: 500,
    matchingPercent: 95,
    name: "",
    model: "",
    deals: "",
});

// Computed
const filteredCars = computed(() => {
    currentPage.value = 1;
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

// Pagination state
const currentPage = ref(1);

// Computed
const paginatedCars = computed(() => {
    const start = (currentPage.value - 1) * 20;
    const end = start + 20;
    return filteredCars.value.slice(start, end);
});

// Modal state
const isComparisonOpen = ref(false);
const selectedCar = ref<CarData | null>(null);

// Deal options
const dealOptions = [
    { label: "Best Deals", value: "Best Deals" },
    { label: "Worst Deals", value: "Worst Deals" },
    { label: "Not Bad", value: "Not Bad" },
];

// Methods
function resetFilters() {
    currentPage.value = 1;
    filters.value = {
        cutOffPrice: 500,
        matchingPercent: 95,
        name: "",
        model: "",
        deals: "",
    };
}

function openComparison(car: CarData) {
    selectedCar.value = car;
    isComparisonOpen.value = true;
}

function exportBestDealsHandler() {
    exportBestDeals(cars.value);
}

function exportAllDealsHandler() {
    exportAllDeals(cars.value);
}

async function getCars() {
    cars.value = [];
    isLoading.value = true;
    let retries = 0;
    while (true) {
        console.log(`Starting with cursor - ${cursor.value}`);
        if (retries === 5) {
            isLoading.value = false;
            break;
        }
        try {
            const response = await $fetch<CarsResponse>("/api/cars", {
                query: {
                    cursor: cursor.value,
                    limit: limit.value,
                    cut_off_price: filters.value.cutOffPrice,
                    percentage_limit: filters.value.matchingPercent,
                    domain: props.domain,
                },
            });
            console.log(response);

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

            cursor.value = response.next_cursor;
            retries = 0;
        } catch (err) {
            console.log(err);
            retries += 1;
            break;
        }
    }

    isLoading.value = false;
    return cars;
}

onMounted(async () => {
    isLoading.value = true;
    console.log("Starting...");
    await getCars();
});
</script>
