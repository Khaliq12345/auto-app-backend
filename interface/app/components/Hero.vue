<template>
  <div class="text-center space-y-4">
    <h1 class="text-4xl font-bold text-gray-900 dark:text-white">
      Welcome to Auto App
    </h1>
    <p class="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
      Discover the best car deals from multiple platforms with real-time comparisons and analytics.
    </p>

    <!-- Platform Dropdown -->
    <div class="flex justify-center">
      <UDropdownMenu
        :items="platformItems"
        :disabled="isLoading"
      >
        <UButton
          color="primary"
          variant="solid"
          :disabled="isLoading"
          :loading="isLoading"
        >
          <template #leading>
            <UIcon name="i-heroicons-globe-alt" />
          </template>
          Select Platform
          <template #trailing>
            <UIcon name="i-heroicons-chevron-down" />
          </template>
        </UButton>

        <template #item="{ item }">
          <ULink
            :to="item.to"
            class="flex items-center gap-2 w-full px-2 py-1.5 text-sm"
          >
            <UIcon :name="item.icon" class="w-4 h-4" />
            {{ item.label }}
          </ULink>
        </template>
      </UDropdownMenu>
    </div>

    <!-- Loading Progress -->
    <div v-if="isLoading && currentOffset > 0" class="text-sm text-gray-500">
      Loading data... ({{ currentOffset }} items loaded)
    </div>
  </div>
</template>

<script setup lang="ts">
// Props for loading state and progress
interface Props {
  isLoading?: boolean;
  currentOffset?: number;
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  currentOffset: 0,
});


const platformItems = [
  {
    label: 'La Centrale',
    to: '/lacentrale',
    icon: 'i-heroicons-building-storefront',
  },
  {
    label: 'Le Bon Coin',
    to: '/leboncoin',
    icon: 'i-heroicons-shopping-bag',
  }
];
</script>
