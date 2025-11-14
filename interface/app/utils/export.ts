import { toRaw } from "vue";
import type { CarData } from "~/types";

export function getFilteredCars(
  cars: CarData[],
  filters: { matchingPercent: number | null },
  state: "all" | "best",
  defaultThreshold: number = 95,
): CarData[] {
  if (state === "all") {
    return cars;
  }

  // Filter cars based on matching percentage threshold
  const threshold = filters.matchingPercent ?? defaultThreshold;
  return cars.filter((car) => car.best_match_percentage >= threshold);
}

type CsvPrimitive = string | number | boolean | null;

function sanitizeCar(car: CarData): Record<string, CsvPrimitive> {
  const { comparisons, ...rest } = toRaw(car) as CarData;

  return Object.fromEntries(
    Object.entries(rest).map(([key, value]) => [key, formatValue(value)]),
  );
}

function formatValue(value: unknown): CsvPrimitive {
  if (value === null || value === undefined) {
    return null;
  }

  if (typeof value === "object") {
    return JSON.stringify(value);
  }

  if (value instanceof Date) {
    return value.toISOString();
  }

  return value as CsvPrimitive;
}

export function exportToCSV(
  data: Record<string, CsvPrimitive>[],
  filename: string,
) {
  if (data.length === 0) {
    return;
  }

  // Get all unique keys from the first item
  const headers = Object.keys(data[0] as object);

  // Create CSV content
  const csvContent = [
    headers.join(","),
    ...data.map((item) =>
      headers
        .map((header) => {
          const value = item[header];
          // Escape commas and quotes in values
          if (
            typeof value === "string" &&
            (value.includes(",") || value.includes('"'))
          ) {
            return `"${value.replace(/"/g, '""')}"`;
          }
          return String(value ?? "");
        })
        .join(","),
    ),
  ].join("\n");

  // Create and download the file
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.setAttribute("href", url);
  link.setAttribute("download", filename);
  link.style.visibility = "hidden";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

export function exportBestDeals(
  cars: CarData[],
  filters: { matchingPercent: number | null },
  defaultThreshold: number = 95,
) {
  const filteredCars = getFilteredCars(cars, filters, "best", defaultThreshold);
  const sanitizedCars = filteredCars.map(sanitizeCar);
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, -5);
  const filename = `best-deals-${timestamp}.csv`;
  exportToCSV(sanitizedCars, filename);
}

export function exportAllDeals(cars: CarData[]) {
  const filteredCars = getFilteredCars(cars, { matchingPercent: null }, "all");
  const sanitizedCars = filteredCars.map(sanitizeCar);
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, -5);
  const filename = `all-deals-${timestamp}.csv`;
  exportToCSV(sanitizedCars, filename);
}
