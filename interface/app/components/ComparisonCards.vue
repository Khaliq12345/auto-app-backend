<template>
    <div class="space-y-6">
        <div v-if="slug" class="text-center mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ slug }}</h3>
        </div>
        <ComparisonCard
            v-if="groupedData.lacentrale.length > 0"
            :comparisons="groupedData.lacentrale"
            slug="lacentrale"
        />

        <ComparisonCard
            v-if="groupedData.leboncoin.length > 0"
            :comparisons="groupedData.leboncoin"
            slug="leboncoin"
        />
    </div>
</template>

<script setup lang="ts">
import type { ComparisonItem, GroupedComparisons } from "~/types";

interface Props {
    comparisons: ComparisonItem[];
    slug?: string;
}

const props = defineProps<Props>();

// Test data
const testComparisons: ComparisonItem[] = [
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
        link: "https://www.leboncoin.fr/auto-occasion-annonce-12345.html",
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
            "Similar electric van with comparable specifications.",
    },
];

// Function to group data by domain
function groupByDomain(comparisons: ComparisonItem[]): GroupedComparisons {
    return comparisons.reduce(
        (acc, item) => {
            if (item.domain === "https://www.lacentrale.fr/") {
                acc.lacentrale.push(item);
            } else if (item.domain === "https://www.leboncoin.fr/") {
                acc.leboncoin.push(item);
            }
            return acc;
        },
        {
            lacentrale: [] as ComparisonItem[],
            leboncoin: [] as ComparisonItem[],
        },
    );
}

// Computed property to group the data
const groupedData = computed(() => {
    // Use props.comparisons if provided, otherwise use test data
    const dataToGroup =
        props.comparisons?.length > 0 ? props.comparisons : testComparisons;
    return groupByDomain(dataToGroup);
});
</script>
