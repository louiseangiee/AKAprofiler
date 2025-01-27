<template>
  <div class="flex flex-wrap">
    <div class="w-full lg:w-4/12 px-4">
      <CardProfile />
    </div>
    <div class="w-full lg:w-8/12 px-4">
      <CardDetails />
    </div>
  </div>
</template>
<script>
import CardDetails from "@/components/Cards/CardDetails.vue";
import CardProfile from "@/components/Cards/CardProfile.vue";

export default {
  components: {
    CardDetails,
    CardProfile,
  },
};
</script>
