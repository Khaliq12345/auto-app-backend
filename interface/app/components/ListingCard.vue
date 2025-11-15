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

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <UCard
                    v-for="car in filteredCars"
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
import type { CarData, Filters } from "~/types";

// Données de test
const testCars: CarData[] = [
    {
        make: "CORVETTE",
        model: "C8 Corvette Stingray Coupé Callaway Edition",
        version: "Edition",
        color: "schwarz",
        mileage: 5000,
        fuel_type: "Benzin",
        updated_at: "2025-11-09T19:30:07.376215",
        price_with_tax: 135000.0022,
        year_from: 2025,
        year_to: 2025,
        car_url:
            "https://auto-brass.com/decouvrir-les-occasions?freier_text=2990006",
        price_with_no_tax: 113445.38,
        id: "2990006",
        lacentrale: true,
        leboncoin: false,
        comparisons: [
            {
                id: "1762713078_2990006",
                link: "https://www.leboncoin.fr/voitures/2345678903.htm",
                name: "CHEVROLET CORVETTE",
                image: "https://img.leboncoin.fr/api/v1/lbcpb1/images/corvette123.jpg",
                price: 125000,
                domain: "https://www.leboncoin.fr/",
                mileage: 8000,
                deal_type: "GOOD_DEAL",
                fuel_type: "BENZIN",
                created_at: "2025-11-09T18:31:53.886335+00:00",
                updated_at: "2025-11-09T19:30:23.451847",
                car_metadata: "C8 Stingray Coupé",
                parent_car_id: "2990006",
                boite_de_vitesse: "AUTO",
                matching_percentage: 88,
                matching_percentage_reason:
                    "Similar Corvette C8 model with comparable specifications and mileage.",
            },
            {
                id: "1762713079_2990006",
                link: "https://www.lacentrale.fr/auto-occasion-annonce-corvette456.html",
                name: "CHEVROLET CORVETTE C8",
                image: "https://pictures.lacentrale.fr/classifieds/corvette456_STANDARD_0.jpg",
                price: 140000,
                domain: "https://www.lacentrale.fr/",
                mileage: 3000,
                deal_type: "AVERAGE_DEAL",
                fuel_type: "BENZIN",
                created_at: "2025-11-09T18:31:53.886335+00:00",
                updated_at: "2025-11-09T19:30:23.451847",
                car_metadata: "C8 Stingray Z51",
                parent_car_id: "2990006",
                boite_de_vitesse: "AUTO",
                matching_percentage: 92,
                matching_percentage_reason:
                    "Very similar Corvette C8 with lower mileage but higher trim level.",
            },
        ],
        lowest_price: 0,
        average_price: 0,
        average_price_based_on_best_match: 0,
        price_difference_with_avg_price: -135000.0022,
        card_color: "red",
        best_match_percentage: 0,
        best_match_link: null,
    },
    {
        make: "BMW",
        model: "M3 Competition",
        version: "G80",
        color: "Alpine White",
        mileage: 15000,
        fuel_type: "Benzin",
        updated_at: "2025-11-09T18:30:07.376215",
        price_with_tax: 85000,
        year_from: 2023,
        year_to: 2023,
        car_url:
            "https://auto-brass.com/decouvrir-les-occasions?freier_text=2990007",
        price_with_no_tax: 71428.57,
        id: "2990007",
        lacentrale: true,
        leboncoin: true,
        comparisons: [
            {
                id: "1762713077_9143559",
                link: "https://www.lacentrale.fr/auto-occasion-annonce-69116222960.html",
                name: "BMW M3",
                image: "https://pictures.lacentrale.fr/classifieds/E116081536_STANDARD_0.jpg",
                price: 82000,
                domain: "https://www.lacentrale.fr/",
                mileage: 18000,
                deal_type: "GOOD_DEAL",
                fuel_type: "BENZIN",
                created_at: "2025-11-09T18:31:53.886335+00:00",
                updated_at: "2025-11-09T19:30:23.451847",
                car_metadata: "M3 Competition G80",
                parent_car_id: "9143559",
                boite_de_vitesse: "AUTO",
                matching_percentage: 95,
                matching_percentage_reason:
                    "Very similar BMW M3 models with close mileage and specifications.",
            },
        ],
        lowest_price: 82000,
        average_price: 85000,
        average_price_based_on_best_match: 83500,
        price_difference_with_avg_price: 0,
        card_color: "green",
        best_match_percentage: 95,
        best_match_link:
            "https://www.lacentrale.fr/auto-occasion-annonce-69116222960.html",
    },
    {
        make: "AUDI",
        model: "RS6 Avant",
        version: "C8",
        color: "Nardo Grey",
        mileage: 25000,
        fuel_type: "Benzin",
        updated_at: "2025-11-09T17:30:07.376215",
        price_with_tax: 95000,
        year_from: 2022,
        year_to: 2022,
        car_url:
            "https://auto-brass.com/decouvrir-les-occasions?freier_text=2990008",
        price_with_no_tax: 79831.93,
        id: "2990008",
        lacentrale: false,
        leboncoin: true,
        comparisons: [
            {
                id: "1762713080_2990008",
                link: "https://www.lacentrale.fr/auto-occasion-annonce-audi789.html",
                name: "AUDI RS6 AVANT",
                image: "https://pictures.lacentrale.fr/classifieds/audi789_STANDARD_0.jpg",
                price: 89000,
                domain: "https://www.lacentrale.fr/",
                mileage: 30000,
                deal_type: "VERY_GOOD_DEAL",
                fuel_type: "BENZIN",
                created_at: "2025-11-09T18:31:53.886335+00:00",
                updated_at: "2025-11-09T19:30:23.451847",
                car_metadata: "RS6 Avant C8 Performance",
                parent_car_id: "2990008",
                boite_de_vitesse: "AUTO",
                matching_percentage: 90,
                matching_percentage_reason:
                    "Excellent match for Audi RS6 Avant with similar specifications and competitive pricing.",
            },
            {
                id: "1762713081_2990008",
                link: "https://www.leboncoin.fr/voitures/2345678904.htm",
                name: "AUDI RS6",
                image: null,
                price: 98000,
                domain: "https://www.leboncoin.fr/",
                mileage: 20000,
                deal_type: "GOOD_DEAL",
                fuel_type: "BENZIN",
                created_at: "2025-11-09T18:31:53.886335+00:00",
                updated_at: "2025-11-09T19:30:23.451847",
                car_metadata: "RS6 Avant Quattro",
                parent_car_id: "2990008",
                boite_de_vitesse: "AUTO",
                matching_percentage: 85,
                matching_percentage_reason:
                    "Good match for Audi RS6 with lower mileage but slightly higher price.",
            },
        ],
        lowest_price: 0,
        average_price: 0,
        average_price_based_on_best_match: 0,
        price_difference_with_avg_price: -95000,
        card_color: "yellow",
        best_match_percentage: 0,
        best_match_link: null,
    },
    {
        make: "PORSCHE",
        model: "911 Turbo S",
        version: "992",
        color: "Guards Red",
        mileage: 12000,
        fuel_type: "Benzin",
        updated_at: "2025-11-09T16:30:07.376215",
        price_with_tax: 220000,
        year_from: 2023,
        year_to: 2023,
        car_url:
            "https://auto-brass.com/decouvrir-les-occasions?freier_text=2990009",
        price_with_no_tax: 184873.95,
        id: "2990009",
        lacentrale: true,
        leboncoin: true,
        comparisons: [
            {
                id: "1762713082_2990009",
                link: "https://www.lacentrale.fr/auto-occasion-annonce-porsche123.html",
                name: "PORSCHE 911 TURBO S",
                image: "https://pictures.lacentrale.fr/classifieds/porsche123_STANDARD_0.jpg",
                price: 215000,
                domain: "https://www.lacentrale.fr/",
                mileage: 15000,
                deal_type: "GOOD_DEAL",
                fuel_type: "BENZIN",
                created_at: "2025-11-09T18:31:53.886335+00:00",
                updated_at: "2025-11-09T19:30:23.451847",
                car_metadata: "911 Turbo S 992 PDK",
                parent_car_id: "2990009",
                boite_de_vitesse: "AUTO",
                matching_percentage: 94,
                matching_percentage_reason:
                    "Excellent match for Porsche 911 Turbo S with very similar specifications and competitive pricing.",
            },
            {
                id: "1762713083_2990009",
                link: "https://www.leboncoin.fr/voitures/2345678905.htm",
                name: "PORSCHE 911",
                image: "https://img.leboncoin.fr/api/v1/lbcpb1/images/porsche456.jpg",
                price: 230000,
                domain: "https://www.leboncoin.fr/",
                mileage: 8000,
                deal_type: "AVERAGE_DEAL",
                fuel_type: "BENZIN",
                created_at: "2025-11-09T18:31:53.886335+00:00",
                updated_at: "2025-11-09T19:30:23.451847",
                car_metadata: "911 Turbo S Cabriolet",
                parent_car_id: "2990009",
                boite_de_vitesse: "AUTO",
                matching_percentage: 87,
                matching_percentage_reason:
                    "Good match for Porsche 911 Turbo S, cabriolet version with lower mileage but higher price.",
            },
        ],
        lowest_price: 215000,
        average_price: 222500,
        average_price_based_on_best_match: 217500,
        price_difference_with_avg_price: -2500,
        card_color: "green",
        best_match_percentage: 94,
        best_match_link:
            "https://www.lacentrale.fr/auto-occasion-annonce-porsche123.html",
    },
];

// Reactive data
const filters = ref<Filters>({
    cutOffPrice: null,
    matchingPercent: null,
    name: "",
    model: "",
    deals: "",
});

const dealOptions = [
    { label: "Best Deals", value: "Best Deals" },
    { label: "Worst Deals", value: "Worst Deals" },
    { label: "Not Bad", value: "Not Bad" },
];

const isComparisonOpen = ref(false);
const selectedCar = ref<CarData | null>(null);

const filteredCars = computed(() => {
    let result = [...testCars];

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
            console.log(dealType);
            if (dealType === "Best Deals") return car.card_color === "green";
            if (dealType === "Worst Deals") return car.card_color === "red";
            if (dealType === "Not Bad") return car.card_color === "yellow";
            return true;
        });
    }

    return result;
});

// Methodes de reset
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
