import type { CarsResponse, CarsResponseDetails } from "~/types";

export default async function getCars(
  cutOffPrice: number,
  percentageLimit: number,
  domain: string | undefined,
  offset: number,
) {
  const limit = 20;
  const cars = [];
  while (true) {
    console.log("offset - ", offset);
    try {
      const response = await $fetch<CarsResponse>("/api/cars", {
        query: {
          offset,
          limit: limit,
          cut_off_price: cutOffPrice,
          percentage_limit: percentageLimit,
          domain: domain,
        },
      });
      console.log(response);

      const detailsSource = Array.isArray(response.details)
        ? response.details
        : (response.details as CarsResponseDetails | undefined)?.data;

      const responseDetails = Array.isArray(detailsSource) ? detailsSource : [];

      if (!responseDetails.length) {
        break;
      }

      cars.push(...responseDetails);

      if (responseDetails.length < limit) {
        break;
      }

      offset += limit;
    } catch (err) {
      console.log(err);
      break;
    }
  }
  return cars;
}
