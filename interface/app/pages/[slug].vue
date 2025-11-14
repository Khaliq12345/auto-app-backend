<template>
    <div class="min-h-screen bg-background">
        <div class="container mx-auto px-4 py-8 space-y-8">
            <Hero :is-loading="heroIsLoading" :current-offset="heroCurrentOffset" />

            <Header />

            <ScrapingCard />

            <ListingCard :domain="domain" />

            <!-- Details Button and Modal -->
            <div class="flex justify-center">
                <UButton
                    @click="open = true"
                    size="lg"
                    icon="i-heroicons-eye"
                    class="px-8"
                >
                    View Details
                </UButton>
            </div>

            <!-- Details Modal with ComparisonCards -->
            <UModal v-model:open="open" title="Comparison Details">
                <template #body>
                    <ComparisonCards :comparisons="sampleComparisons" />
                </template>
            </UModal>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { ComparisonItem } from "~/types";

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

const open = ref(false);

// Loading state and progress tracking for Hero component
const heroIsLoading = ref(false);
const heroCurrentOffset = ref(0);

// Use domain from slug
const domain = getDomainFromSlug(slug);

// Use composables with domain
const { cars, isLoading, fetchError } = useCarFetching(domain);

// Sync loading states for Hero component
watch(isLoading, (newValue) => {
  heroIsLoading.value = newValue;
});

watch(cars, () => {
  heroCurrentOffset.value = cars.value.length;
}, { immediate: true });

onMounted(() => {
  // Domain is now passed to useCarFetching automatically
  console.log('Page loaded with domain:', domain);
});
const sampleComparisons: ComparisonItem[] = [
    {
        id: "1762713077_9143559",
        link: "https://www.lacentrale.fr/auto-occasion-annonce-69116222960.html",
        name: "MAXUS EDELIVER9",
        image: "https://pictures.lacentrale.fr/classifieds/E116081536_STANDARD_0.jpg?format=webp&size=352x264&watermark=lc&signature=1c2039874873bf1455543ea2b9a772389285cfa3418d906120f4c381",
        price: 37908,
        domain: "https://www.lacentrale.fr/",
        mileage: 10,
        deal_type: "VERY_GOOD_DEAL",
        fuel_type: "ELECTRIC",
        created_at: "2025-11-09T18:31:53.886335+00:00",
        updated_at: "2025-11-09T19:30:23.451847",
        car_metadata: "FOURGON L3H2 72 KWH",
        parent_car_id: "9143559",
        boite_de_vitesse: "AUTO",
        matching_percentage: 95,
        matching_percentage_reason:
            "The cars have the same make and model, with a very similar mileage. The version is also highly similar, with 'eDELIVER9 L3 Fahrgestell mit Schutz Pritschenaufbau' being a specific configuration of the 'EDELIVER9' van, and 'FOURGON L3H2 72 KWH' refers to similar van dimensions (L3) and electric specifications. This results in a high overall match.",
    },
    {
        id: "1762713100_9143559",
        link: "https://www.lacentrale.fr/auto-occasion-annonce-69116222960.html",
        name: "MAXUS EDELIVER9",
        image: null,
        price: 41990,
        domain: "https://www.lacentrale.fr/",
        mileage: 100,
        deal_type: "VERY_GOOD_DEAL",
        fuel_type: "ELECTRIC",
        created_at: "2025-11-09T18:31:53.886335+00:00",
        updated_at: "2025-11-09T19:30:23.451847",
        car_metadata: "FOURGON 72 L3H2 KWH",
        parent_car_id: "9143559",
        boite_de_vitesse: "AUTO",
        matching_percentage: 90,
        matching_percentage_reason:
            "The cars have the same make (20%), very similar models (20%), a similar version when considering 'eDELIVER9 L3 Fahrgestell mit Schutz Pritschenaufbau' and 'EDELIVER9 FOURGON 72 L3H2' (10%), and a mileage that is relatively close (40%).",
    },
    {
        id: "1762713101_9143560",
        link: "https://www.leboncoin.fr/voitures/2345678901.htm",
        name: "RENAULT KANGOO",
        image: "https://i.pinimg.com/1200x/89/c4/5c/89c45c520acbfac39152c1f1c3e6ed66.jpg",
        price: 25000,
        domain: "https://www.leboncoin.fr/",
        mileage: 50000,
        deal_type: "GOOD_DEAL",
        fuel_type: "ELECTRIC",
        created_at: "2025-11-09T18:31:53.886335+00:00",
        updated_at: "2025-11-09T19:30:23.451847",
        car_metadata: "FOURGON ELECTRIQUE",
        parent_car_id: "9143560",
        boite_de_vitesse: "AUTO",
        matching_percentage: 85,
        matching_percentage_reason:
            "Similar electric van with comparable specifications and good value proposition.",
    },
    {
        id: "1762713102_9143561",
        link: "https://www.leboncoin.fr/voitures/2345678902.htm",
        name: "PEUGEOT PARTNER",
        image: null,
        price: 22000,
        domain: "https://www.leboncoin.fr/",
        mileage: 75000,
        deal_type: "AVERAGE_DEAL",
        fuel_type: "ELECTRIC",
        created_at: "2025-11-09T18:31:53.886335+00:00",
        updated_at: "2025-11-09T19:30:23.451847",
        car_metadata: "FOURGON ELECTRIQUE COMPACT",
        parent_car_id: "9143561",
        boite_de_vitesse: "AUTO",
        matching_percentage: 80,
        matching_percentage_reason:
            "Electric van with decent specifications but higher mileage affects the overall match score.",
    },
];
</script>
