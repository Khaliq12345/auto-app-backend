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
                        <UCard
                            class="bg-background border-border/40 shadow-sm"
                            :class="
                                metric.color ? `border-${metric.color}-500` : ''
                            "
                        >
                            <div class="p-4">
                                <div class="flex items-start gap-3">
                                    <UIcon
                                        :name="metric.icon"
                                        :class="
                                            metric.color
                                                ? `text-${metric.color}-500`
                                                : 'text-primary'
                                        "
                                        class="text-xl"
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
                                        <p
                                            v-if="metric.subtitle"
                                            class="text-xs text-gray-500"
                                        >
                                            {{ metric.subtitle }}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </UCard>
                    </template>
                </UPageGrid>
            </div>
        </UCard>
        <div>
            <UFileUpload
                v-model="files"
                accept=".xls,.xlsx,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                class="w-full min-h-48"
            />

            <UButton
                class="items-center justify-center w-full mt-6"
                @click="uploadFile"
            >
                Upload a new file
            </UButton>
        </div>
    </UPageCard>
</template>

<script setup lang="ts">
import type { ScrapingStatusResponse } from "~/types";
const files = ref<any[]>([]);

const uploadFile = async () => {
    if (!files.value) return alert("Aucun fichier sélectionné");

    const file = files.value[0];
    const formData = new FormData();
    formData.append("file", file);

    await $fetch("/api/upload-file", {
        method: "POST",
        body: formData,
    });

    alert("Upload OK");
    files.value = [];
};

// Fetch scraping status from API with error handling
const { data: scrapingStatus, error: fetchError } =
    await $fetch<ScrapingStatusResponse>("/api/status")
        .then((data) => ({ data, error: null }))
        .catch((error) => ({
            data: null,
            error: error.message || "Failed to fetch status",
        }));

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

// Use API data or fallback to default values
const latestStatus = scrapingStatus?.details?.data?.[0];
const status = latestStatus?.status || "success";
const total_completed = latestStatus?.total_completed ?? 0;
const total_running = latestStatus?.total_running ?? 0;
const started_at = latestStatus?.started_at ?? latestStatus?.created_at;
const stopped_at = latestStatus?.stopped_at ?? started_at;
const last_updated = stopped_at ?? new Date().toISOString();

// Calculate progress based on completed vs running totals
const progress =
    total_running > 0
        ? Math.min(100, Math.round((total_completed / total_running) * 100))
        : 0;
const hasErrors = Boolean(latestStatus?.errors);

const badgeColor = fetchError
    ? "error"
    : (statusColor[status as keyof typeof statusColor] ?? "neutral");
const badgeLabel = fetchError
    ? "API Error"
    : (statusLabel[status as keyof typeof statusLabel] ?? status);

const metrics = [
    {
        label: "Total completed",
        icon: "i-heroicons-check-circle",
        value: fetchError ? "N/A" : total_completed.toLocaleString(),
        color: fetchError ? "error" : undefined,
    },
    {
        label: "Total running",
        icon: "i-heroicons-bolt",
        value: fetchError ? "N/A" : total_running.toLocaleString(),
        color: fetchError ? "error" : undefined,
    },
    {
        label: "Progress",
        icon: "i-heroicons-chart-bar",
        value: fetchError ? "N/A" : `${progress}%`,
        color: fetchError
            ? "error"
            : hasErrors
              ? "error"
              : progress === 100
                ? "success"
                : "info",
    },
    {
        label: "Last updated",
        icon: "i-heroicons-clock",
        value: fetchError ? "N/A" : new Date(last_updated).toLocaleString(),
        subtitle: fetchError
            ? `🚨 API Error: ${fetchError}`
            : hasErrors
              ? `⚠️ Errors: ${latestStatus?.errors ?? "Unknown issue"}`
              : started_at
                ? `Started: ${new Date(started_at).toLocaleString()}`
                : "No errors",
        color: fetchError ? "error" : undefined,
    },
];
</script>
