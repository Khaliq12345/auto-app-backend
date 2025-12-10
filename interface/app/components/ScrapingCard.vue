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

        <!-- Desktop layout-->
        <section class="hidden sm:block">
            <UPageGrid class="gap-4" :columns="{ sm: 1, md: 2, lg: 3 }">
                <UCard
                    v-for="item in statusItems"
                    :key="item.id || item.started_at || item.created_at"
                    class="border shadow-sm"
                    :class="statusStyle(item.status).card"
                >
                    <div class="flex items-start gap-3">
                        <UIcon
                            :name="statusStyle(item.status).icon"
                            :class="statusStyle(item.status).iconClass"
                            class="text-xl"
                        />
                        <div class="space-y-1">
                            <p class="text-sm font-medium ui:text-gray-600">
                                Status
                            </p>
                            <p class="text-lg font-semibold capitalize">
                                {{ statusLabel(item.status) }}
                            </p>
                            <p class="text-xs text-gray-600">
                                Started:
                                {{
                                    formatDate(
                                        item.started_at || item.created_at,
                                    )
                                }}
                            </p>
                            <p
                                class="text-xs text-gray-600"
                                v-if="item.stopped_at"
                            >
                                Stopped: {{ formatDate(item.stopped_at) }}
                            </p>
                        </div>
                    </div>

                    <div class="mt-4 grid grid-cols-2 gap-3 text-sm">
                        <div class="space-y-0.5">
                            <p class="text-gray-600">Completed</p>
                            <p class="text-base font-semibold">
                                {{ item.total_completed ?? 0 }}
                            </p>
                        </div>
                        <div class="space-y-0.5">
                            <p class="text-gray-600">Running</p>
                            <p class="text-base font-semibold">
                                {{ item.total_running ?? 0 }}
                            </p>
                        </div>
                        <div class="space-y-0.5">
                            <p class="text-gray-600">Progress</p>
                            <p class="text-base font-semibold">
                                {{ formatProgress(item) }}
                            </p>
                        </div>
                        <div class="space-y-0.5" v-if="item.errors">
                            <p class="text-gray-600">Errors</p>
                            <p class="text-base font-semibold text-error-600">
                                {{ item.errors }}
                            </p>
                        </div>
                    </div>
                </UCard>
            </UPageGrid>
        </section>

        <!-- Mobile layout -->
        <section class="sm:hidden">
            <UAccordion :items="mobileAccordionItems" type="multiple">
                <template #body="{ item }">
                    <div
                        class="p-3 rounded-lg border"
                        :class="statusStyle(item.raw?.status).card"
                    >
                        <div class="grid grid-cols-2 gap-3 text-sm">
                            <div class="space-y-0.5">
                                <p class="text-gray-600">Completed</p>
                                <p class="text-base font-semibold">
                                    {{ item.raw?.total_completed ?? 0 }}
                                </p>
                            </div>
                            <div class="space-y-0.5">
                                <p class="text-gray-600">Running</p>
                                <p class="text-base font-semibold">
                                    {{ item.raw?.total_running ?? 0 }}
                                </p>
                            </div>
                            <div class="space-y-0.5">
                                <p class="text-gray-600">Progress</p>
                                <p class="text-base font-semibold">
                                    {{ formatProgress(item.raw) }}
                                </p>
                            </div>
                            <div class="space-y-0.5" v-if="item.raw?.errors">
                                <p class="text-gray-600">Errors</p>
                                <p
                                    class="text-base font-semibold text-error-600"
                                >
                                    {{ item.raw.errors }}
                                </p>
                            </div>
                        </div>
                        <div class="mt-3 text-xs text-gray-500 space-y-1">
                            <p>
                                Started:
                                {{
                                    formatDate(
                                        item.raw?.started_at ||
                                            item.raw?.created_at,
                                    )
                                }}
                            </p>
                            <p v-if="item.raw?.stopped_at">
                                Stopped: {{ formatDate(item.raw.stopped_at) }}
                            </p>
                        </div>
                    </div>
                </template>
            </UAccordion>
        </section>
        <div>
            <URadioGroup
                v-model="uploadType"
                :items="uploadTypeItems"
                :orientation="isMobile ? 'vertical' : 'horizontal'"
                class="mb-4"
            />

            <UFileUpload
                v-model="files"
                accept=".xls,.xlsx,.json,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/json"
                class="w-full min-h-48"
            />

            <UButton
                class="items-center justify-center w-full mt-6"
                :loading="isUploading"
                :disabled="isUploading"
                @click="uploadFile"
            >
                {{ isUploading ? "Upload en cours..." : "Upload a new file" }}
            </UButton>
        </div>

        <!-- Start Scraper Collapsible -->
        <UCollapsible class="flex flex-col gap-2 mt-6">
            <UButton
                class="group"
                label="Start Scraper"
                color="neutral"
                variant="subtle"
                trailing-icon="i-lucide-chevron-down"
                :ui="{
                    trailingIcon:
                        'group-data-[state=open]:rotate-180 transition-transform duration-200',
                }"
                block
            />

            <template #content>
                <UCard class="mt-2">
                    <StartScraperForm />
                </UCard>
            </template>
        </UCollapsible>
    </UPageCard>
</template>

<script setup lang="ts">
import type { ScrapingStatusItem, ScrapingStatusResponse } from "~/types";
import type { AccordionItem, RadioGroupItem } from "@nuxt/ui";
import { useResponsive } from "../../composables/useResponsive";

const toast = useToast();
const files = ref<File | null>(null);
const uploadType = ref("Input File");
const isUploading = ref(false);

// Responsive detection using composable
const { isMobile } = useResponsive();

const uploadTypeItems: RadioGroupItem[] = [
    { label: "Input File", value: "Input File" },
    { label: "Leboncoin cookies", value: "Leboncoin cookies" },
    { label: "Leboncoin Headers", value: "Leboncoin Headers" },
    { label: "Lacentrale Cookies", value: "Lacentrale Cookies" },
    { label: "Lacentrale Headers", value: "Lacentrale Headers" },
];

const uploadFile = async () => {
    if (!files.value) {
        toast.add({
            title: "Aucun fichier sélectionné",
            description: "Veuillez sélectionner un fichier avant de continuer.",
            icon: "i-heroicons-exclamation-triangle",
            color: "warning",
        });
        return;
    }

    isUploading.value = true;

    try {
        const file = files.value;
        const formData = new FormData();
        formData.append("file", file);
        formData.append("upload_type", uploadType.value);

        const response = await $fetch<{ success: boolean; error?: string }>(
            "/api/upload-file",
            {
                method: "POST",
                body: formData,
            },
        );

        if (response.success) {
            toast.add({
                title: "Upload réussi",
                description: `Le fichier a été uploadé avec succès.`,
                icon: "i-heroicons-check-circle",
                color: "success",
            });
            files.value = null;
        } else {
            toast.add({
                title: "Erreur lors de l'upload",
                description:
                    response.error || "Une erreur inconnue s'est produite.",
                icon: "i-heroicons-x-circle",
                color: "error",
            });
        }
    } catch (error: any) {
        toast.add({
            title: "Erreur lors de l'upload",
            description: error?.message || "Une erreur réseau s'est produite.",
            icon: "i-heroicons-x-circle",
            color: "error",
        });
    } finally {
        isUploading.value = false;
    }
};

// Fetch scraping status from API with error handling
const { data: scrapingStatus, error: fetchError } =
    await $fetch<ScrapingStatusResponse>("/api/status")
        .then((data) => ({ data, error: null }))
        .catch((error) => ({
            data: null,
            error: error.message || "Failed to fetch status",
        }));

const statusItems = computed<ScrapingStatusItem[]>(
    () => scrapingStatus?.details?.data ?? [],
);

// accordion items for mobile
const mobileAccordionItems = computed(() =>
    statusItems.value.map((item, index) => ({
        label: `${statusLabel(item.status)} · ${item.total_completed ?? 0}/${item.total_running ?? 0}`,
        icon: statusStyle(item.status).icon,
        value: String(item.id ?? index),
        raw: item,
        ui: {
            trigger: statusStyle(item.status).triggerClass,
        },
    })),
);

const statusMap = {
    success: {
        card: "bg-success-50 border-success-200",
        icon: "i-lucide-check-circle-2",
        iconClass: "text-success-600",
        badge: "success",
        triggerClass: "text-success-700 bg-success-50 hover:bg-success-100",
    },
    failed: {
        card: "bg-error-50 border-error-200",
        icon: "i-lucide-x-circle",
        iconClass: "text-error-600",
        badge: "error",
        triggerClass: "text-error-700 bg-error-50 hover:bg-error-100",
    },
    running: {
        card: "bg-info-50 border-info-200",
        icon: "i-lucide-loader-2 animate-spin",
        iconClass: "text-info-600",
        badge: "info",
        triggerClass: "text-info-700 bg-info-50 hover:bg-info-100",
    },
    default: {
        card: "bg-background border-border/50",
        icon: "i-lucide-info",
        iconClass: "text-gray-500",
        badge: "neutral",
        triggerClass: "",
    },
} as const;

const statusLabel = (status?: string) => {
    const map: Record<string, string> = {
        success: "Success",
        failed: "Failed",
        running: "Running",
    };
    return map[status ?? ""] || status || "Unknown";
};

const statusStyle = (status?: string) =>
    statusMap[status as keyof typeof statusMap] ?? statusMap.default;

const primaryStatus = computed(() => statusItems.value?.[0]);

const badgeColor = fetchError
    ? "error"
    : statusStyle(primaryStatus.value?.status).badge;
const badgeLabel = fetchError
    ? "API Error"
    : statusLabel(primaryStatus.value?.status);

function formatDate(value?: string) {
    if (!value) return "N/A";
    return new Date(value).toLocaleString();
}

function formatProgress(item: ScrapingStatusItem) {
    const completed = item.total_completed ?? 0;
    const running = item.total_running ?? 0;
    if (running === 0) return "0%";
    const ratio = Math.min(100, Math.round((completed / running) * 100));
    return `${ratio}%`;
}
</script>
