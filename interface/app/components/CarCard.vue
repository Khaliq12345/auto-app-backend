<template>
    <UCard class="overflow-hidden" :class="getCardColorClass(car.card_color)">
        <div class="space-y-4">
            <!-- Car Header -->
            <div class="flex justify-between items-start">
                <div>
                    <h3 class="font-semibold text-lg">{{ car.make }}</h3>
                    <p class="text-sm text-gray-600">{{ car.model }}</p>
                    <p class="text-xs text-gray-500">{{ car.version }}</p>
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
                    <span class="text-sm text-gray-600">Price with tax:</span>
                    <span class="font-bold text-lg">
                        €{{ car.price_with_tax?.toLocaleString() }}
                    </span>
                </div>
                <div class="flex justify-between items-center">
                    <span class="text-sm text-gray-600"
                        >Price without tax:</span
                    >
                    <span class="font-medium">
                        €{{ car.price_with_no_tax?.toLocaleString() }}
                    </span>
                </div>
            </div>

            <!-- Match Information -->
            <div
                v-if="car.best_match_percentage > 0"
                class="bg-gray-50 p-3 rounded-lg"
            >
                <div class="flex justify-between items-center">
                    <span class="text-sm text-gray-600">Best Match:</span>
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
                    v-if="car.comparisons && car.comparisons.length > 0"
                    @click="$emit('compare', car)"
                    size="sm"
                    icon="i-heroicons-chart-bar-square"
                    class="flex-1"
                >
                    Compare
                </UButton>
            </div>

            <!-- Updated Date -->
            <div class="text-xs text-gray-500 text-center">
                Updated: {{ new Date(car.updated_at).toLocaleDateString() }}
            </div>
        </div>
    </UCard>
</template>

<script setup lang="ts">
import type { CarData } from "~/types";

interface Props {
    car: CarData;
}

defineProps<Props>();
defineEmits<{
    compare: [car: CarData];
}>();

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
