<template>
  <div class="min-h-screen bg-blueGray-100 flex flex-col">
    <sidebar />
    <div class="relative md:ml-64 bg-blueGray-100 flex-1 flex flex-col">
      <admin-navbar />
      <header-stats />
      <div class="px-4 md:px-10 mx-auto w-full -m-24 bg-blueGray-100">
        <router-view />
      </div>
    </div>
  </div>
</template>
<script>
import AdminNavbar from "@/components/Navbars/AdminNavbar.vue";
import Sidebar from "@/components/Sidebar/Sidebar.vue";
import HeaderStats from "@/components/Headers/HeaderStats.vue";

export default {
  name: "admin-layout",
  components: {
    AdminNavbar,
    Sidebar,
    HeaderStats,
  },
};
</script>
