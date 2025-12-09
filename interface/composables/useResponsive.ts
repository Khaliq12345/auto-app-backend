import { ref, watchEffect } from "vue";
import { useWindowSize } from "@vueuse/core";

export interface UseResponsiveOptions {
  desktopMin?: number;
  tabletMin?: number;
}

export function useResponsive(options: UseResponsiveOptions = {}) {
  const { width } = useWindowSize();

  const desktopMin = options.desktopMin ?? 1050;
  const tabletMin = options.tabletMin ?? 1050;

  const isDesktop = ref(false);
  const isMobile = ref(false);
  const responsiveSize = ref("lg");

  watchEffect(() => {
    isDesktop.value = width.value > desktopMin;
    isMobile.value = width.value < tabletMin;
    responsiveSize.value = isMobile.value ? "sm" : "lg";
  });

  return { width, isDesktop, isMobile, responsiveSize };
}
