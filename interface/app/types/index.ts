export interface ComparisonItem {
  id: string;
  link: string;
  name: string;
  image: string | null;
  price: number;
  domain: string;
  mileage: number;
  deal_type: string;
  fuel_type: string;
  created_at: string;
  updated_at: string;
  car_metadata: string;
  parent_car_id: string;
  boite_de_vitesse: string;
  matching_percentage: number;
  matching_percentage_reason: string;
}

export interface CarData {
  make: string;
  model: string;
  version: string;
  color: string;
  mileage: number;
  fuel_type: string;
  updated_at: string;
  price_with_tax: number;
  year_from: number;
  year_to: number;
  car_url: string;
  price_with_no_tax: number;
  id: string;
  lacentrale: boolean;
  leboncoin: boolean;
  comparisons: ComparisonItem[];
  lowest_price: number;
  average_price: number;
  average_price_based_on_best_match: number;
  price_difference_with_avg_price: number;
  card_color: string;
  best_match_percentage: number;
  best_match_link: string | null;
}

export interface Filters {
  cutOffPrice: number | null;
  matchingPercent: number | null;
  name: string;
  model: string;
  deals: string;
  type: string;
}

export interface ScrapingStatus {
  status: string;
  total_completed: number;
  total_running: number;
  stopped_at: string;
  started_at: string;
}

export interface GroupedComparisons {
  lacentrale: ComparisonItem[];
  leboncoin: ComparisonItem[];
}
