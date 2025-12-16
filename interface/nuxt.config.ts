// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },
  css: ["~/assets/css/main.css"],
  modules: ["@nuxt/ui", "@nuxt/fonts", "nuxt-file-storage"],
  fileStorage: {
    mount: "../files/uploads",
  },
  runtimeConfig: {
    // Peut être surchargée par NUXT_BACKEND_URL dans le .env
    backendUrl: "http://157.180.69.73:8500",
    public: {
      // Variables publiques (côté client et serveur)
    },
  },
});
