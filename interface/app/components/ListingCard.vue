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

        <!-- Export Section -->
        <UCard class="p-4">
            <div class="flex gap-4">
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
import type { CarData } from "~/types";

// Configuration
const ITEMS_PER_PAGE = 20;
const DEFAULT_PERCENTAGE_LIMIT = 95;

// Use composables
const { cars, isLoading, fetchError } = useCarFetching();

// Filters
const filters = ref({
    cutOffPrice: null as number | null,
    matchingPercent: null as number | null,
    name: "",
    model: "",
    deals: "",
});

// Computed
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

// Pagination state
const currentPage = ref(1);

// Computed
const paginatedCars = computed(() => {
    const start = (currentPage.value - 1) * ITEMS_PER_PAGE;
    const end = start + ITEMS_PER_PAGE;
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

function exportBestDealsHandler() {
    exportBestDeals(cars.value, filters.value, DEFAULT_PERCENTAGE_LIMIT);
}

function exportAllDealsHandler() {
    exportAllDeals(cars.value);
}
</script>
