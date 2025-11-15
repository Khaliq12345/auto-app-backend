<template>
    <div class="min-h-screen bg-background">
        <div class="container mx-auto px-4 py-8 space-y-8">
            <Hero :is-loading="heroIsLoading" :current-offset="heroCurrentOffset" />

            <Header />

            <ScrapingCard />

            <ListingCard :domain="domain" />
        </div>
    </div>
</template>

<script setup lang="ts">
const route = useRoute();
const slug = route.params.slug as string;

// Function to convert a slug into its corresponding domain URL
function getDomainFromSlug(slug: string): string | undefined {
  if (slug === "lacentrale") {
    return "https://www.lacentrale.fr/";
  }
  if (slug === "leboncoin") {
    return "https://www.leboncoin.fr/";
  }
  return undefined;
}
// Loading state and progress tracking for Hero component
const heroIsLoading = ref(false);
const heroCurrentOffset = ref(0);

// Use domain from slug
const domain = getDomainFromSlug(slug);

// Use composables with domain
const { cars, isLoading, fetchError } = useCarFetching({ domain });

// Sync loading states for Hero component
watch(isLoading, (newValue) => {
  heroIsLoading.value = newValue;
});

watch(cars, () => {
  heroCurrentOffset.value = cars.value.length;
}, { immediate: true });
</script>
