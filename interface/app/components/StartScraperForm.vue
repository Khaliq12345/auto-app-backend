<template>
  <UForm :schema="schema" :state="state" class="space-y-4" @submit="onSubmit">
    <!-- Sites to scrape -->
    <UFormField label="Sites to scrape" name="sites_to_scrape" required>
      <USelectMenu
        v-model="state.sites_to_scrape"
        :items="sitesOptions"
        value-key="value"
        multiple
        placeholder="Select sites to scrape"
        class="w-full"
      />
    </UFormField>

    <!-- Mileage plus/minus -->
    <UFormField label="Mileage +/-" name="mileage_plus_minus">
      <UInput
        v-model.number="state.mileage_plus_minus"
        type="number"
        placeholder="10000 (default)"
        class="w-full"
      />
    </UFormField>

    <!-- Ignore old -->
    <UFormField name="ignore_old">
      <UCheckbox v-model="state.ignore_old" label="Ignore old scraped data" />
    </UFormField>

    <!-- Dev mode -->
    <UFormField name="dev">
      <UCheckbox v-model="state.dev" label="Dev mode (sample 1000 rows)" />
    </UFormField>

    <!-- Car ID -->
    <UFormField label="Car ID" name="car_id">
      <UInput
        v-model="state.car_id"
        placeholder="Leave empty to scrape all"
        class="w-full"
      />
    </UFormField>

    <UButton type="submit" :loading="isLoading" :disabled="isLoading" block>
      {{ isLoading ? "Starting..." : "Start Scraper" }}
    </UButton>
  </UForm>
</template>

<script setup lang="ts">
import * as v from "valibot";
import type { FormSubmitEvent } from "@nuxt/ui";

const toast = useToast();
const isLoading = ref(false);

// Valibot schema
const schema = v.object({
  sites_to_scrape: v.pipe(
    v.array(v.string()),
    v.minLength(1, "Please select at least one site to scrape")
  ),
  mileage_plus_minus: v.optional(v.nullable(v.number())),
  ignore_old: v.optional(v.boolean()),
  dev: v.optional(v.boolean()),
  car_id: v.optional(v.nullable(v.string())),
});

type FormState = v.InferInput<typeof schema>;

const sitesOptions = [
  { label: "Leboncoin", value: "leboncoin" },
  { label: "Lacentrale", value: "lacentrale" },
];

const state = reactive<FormState>({
  sites_to_scrape: [],
  mileage_plus_minus: undefined,
  ignore_old: false,
  dev: false,
  car_id: "",
});

async function onSubmit(event: FormSubmitEvent<FormState>) {
  isLoading.value = true;

  try {
    const response = await $fetch("/api/start-scraper", {
      method: "POST",
      body: {
        sites_to_scrape: state.sites_to_scrape,
        mileage_plus_minus: state.mileage_plus_minus || null,
        ignore_old: state.ignore_old || null,
        dev: state.dev || null,
        car_id: state.car_id || null,
      },
    });

    const result = response as { success: boolean; data?: { task_id?: string }; error?: string };

    if (result.success) {
      toast.add({
        title: "Success",
        description: `Scraper started successfully. Task ID: ${result.data?.task_id}`,
        color: "success",
      });
    } else {
      toast.add({
        title: "Error",
        description: result.error || "Failed to start scraper",
        color: "error",
      });
    }
  } catch (error: unknown) {
    const err = error as { message?: string };
    toast.add({
      title: "Error",
      description: err?.message || "An unexpected error occurred",
      color: "error",
    });
  } finally {
    isLoading.value = false;
  }
}
</script>
