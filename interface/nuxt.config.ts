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
    public: {
      backendUrl: "http://127.0.0.1:5000",
    },
  },
});
