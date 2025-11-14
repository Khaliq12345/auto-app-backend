<template>
    <UPageCard
        title="Scraping status"
        description="Monitor the latest run status and metrics."
        highlight
        spotlight
    >
        <template #description>
            <div class="flex flex-wrap items-center gap-4">
                <span class="text-base font-medium ui:text-gray-900">
                    Monitor the latest run status and metrics.
                </span>
                <UBadge
                    :color="badgeColor"
                    variant="soft"
                    size="sm"
                    class="font-medium"
                >
                    {{ badgeLabel }}
                </UBadge>
            </div>
        </template>

        <UCard class="w-full border-none bg-background/60 shadow-none">
            <div class="p-0">
                <UPageGrid class="gap-4" :columns="{ base: 1, sm: 2 }">
                    <template v-for="metric in metrics" :key="metric.label">
                        <UCard class="bg-background border-border/40 shadow-sm">
                            <div class="p-4">
                                <div class="flex items-start gap-3">
                                    <UIcon
                                        :name="metric.icon"
                                        class="text-xl text-primary"
                                    />
                                    <div class="space-y-1">
                                        <p
                                            class="text-sm font-medium ui:text-gray-600"
                                        >
                                            {{ metric.label }}
                                        </p>
                                        <p
                                            class="text-xl font-semibold tracking-tight ui:text-gray-900"
                                        >
                                            {{ metric.value }}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </UCard>
                    </template>
                </UPageGrid>
            </div>
        </UCard>
    </UPageCard>
</template>

<script setup lang="ts">
const scrapingStatus = {
    status: "success",
    total_completed: 1648,
    total_running: 1648,
    started_at: "2025-07-18T09:15:24.256601",
    stopped_at: "2025-11-13T07:01:24.433036",
};

const statusColor = {
    success: "success",
    failed: "error",
    running: "info",
} as const;

const statusLabel = {
    success: "Success",
    failed: "Failed",
    running: "Running",
} as const;

const badgeColor =
    statusColor[scrapingStatus.status as keyof typeof statusColor] ?? "neutral";
const badgeLabel =
    statusLabel[scrapingStatus.status as keyof typeof statusLabel] ??
    scrapingStatus.status;

const metrics = [
    {
        label: "Total completed",
        icon: "i-heroicons-check-circle",
        value: scrapingStatus.total_completed.toLocaleString(),
    },
    {
        label: "Total running",
        icon: "i-heroicons-bolt",
        value: scrapingStatus.total_running.toLocaleString(),
    },
    {
        label: "Started at",
        icon: "i-heroicons-clock",
        value: new Date(scrapingStatus.started_at).toLocaleString(),
    },
    {
        label: "Stopped at",
        icon: "i-heroicons-stop-circle",
        value: new Date(scrapingStatus.stopped_at).toLocaleString(),
    },
];
</script>
