<template>
    <UCard variant="subtle">
        <UCollapsible>
            <div class="flex items-center justify-between w-full">
                <div class="flex items-center gap-2">
                    <UIcon
                        name="i-heroicons-chart-bar-square"
                        class="text-primary"
                    />
                    <h4 class="font-semibold">{{ slug }}</h4>
                    <UBadge variant="soft" color="primary" size="sm">
                        {{ comparisons.length }} items
                    </UBadge>
                </div>
            </div>

            <template #content>
                <div class="space-y-3 mt-4">
                    <UCard
                        v-for="item in comparisons"
                        :key="item.id"
                        class="border-border/40"
                    >
                        <div class="flex gap-4">
                            <!-- Image Section -->
                            <div class="flex-shrink-0">
                                <img
                                    v-if="item.image"
                                    :src="item.image"
                                    :alt="item.name"
                                    class="w-24 h-24 object-cover rounded-lg border border-border/20"
                                    loading="lazy"
                                />
                                <div
                                    v-else
                                    class="w-24 h-24 bg-muted rounded-lg flex items-center justify-center border border-border/20"
                                >
                                    <UIcon
                                        name="i-heroicons-photo"
                                        class="text-muted-foreground text-2xl"
                                    />
                                </div>
                            </div>

                            <!-- Content Section -->
                            <div class="flex-1 space-y-2">
                                <div class="flex justify-between items-start">
                                    <div>
                                        <h5 class="font-semibold">
                                            {{ item.name }}
                                        </h5>
                                        <p class="text-sm text-gray-600">
                                            {{ item.car_metadata }}
                                        </p>
                                    </div>
                                    <div class="text-right">
                                        <p class="text-lg font-bold">
                                            €{{ item.price?.toLocaleString() }}
                                        </p>
                                    </div>
                                </div>

                                <div
                                    class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm"
                                >
                                    <div>
                                        <span class="text-gray-600"
                                            >Mileage:</span
                                        >
                                        <p class="font-medium">
                                            {{ item.mileage?.toLocaleString() }}
                                            km
                                        </p>
                                    </div>
                                    <div>
                                        <span class="text-gray-600">Fuel:</span>
                                        <p class="font-medium">
                                            {{ item.fuel_type }}
                                        </p>
                                    </div>
                                    <div>
                                        <span class="text-gray-600"
                                            >Gearbox:</span
                                        >
                                        <p class="font-medium">
                                            {{ item.boite_de_vitesse }}
                                        </p>
                                    </div>
                                    <div>
                                        <span class="text-gray-600"
                                            >Match:</span
                                        >
                                        <p class="font-medium">
                                            {{ item.matching_percentage }}%
                                        </p>
                                    </div>
                                </div>

                                <!-- Matching Reason -->
                                <div
                                    v-if="item.matching_percentage_reason"
                                    class="bg-gray-50 p-3 rounded-lg"
                                >
                                    <p class="text-sm text-gray-700">
                                        <strong>Match Reason:</strong>
                                        {{ item.matching_percentage_reason }}
                                    </p>
                                </div>

                                <div
                                    class="flex justify-between items-center pt-2 border-t border-border/20"
                                >
                                    <p class="text-xs text-gray-500">
                                        {{ formatDate(item.updated_at) }}
                                    </p>
                                    <UButton
                                        :to="item.link"
                                        target="_blank"
                                        size="xs"
                                        variant="outline"
                                        icon="i-heroicons-arrow-top-right-on-square"
                                    >
                                        View Listing
                                    </UButton>
                                </div>
                            </div>
                        </div>
                    </UCard>
                </div>
            </template>
        </UCollapsible>
    </UCard>
</template>

<script setup lang="ts">
import type { ComparisonItem } from "~/types";

defineProps<{
    comparisons: ComparisonItem[];
    slug: string;
}>();

function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleString();
}
</script>
