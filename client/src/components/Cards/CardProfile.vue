<template>
  <div
    class="relative flex flex-col min-w-0 break-words bg-blueGray-100 w-full mb-6 shadow-lg rounded-lg border-0"
  >
  <div class="rounded-t bg-white mb-0 px-6 py-6">
    <div class="text-center flex justify-between">
        <h6 class="text-blueGray-700 text-xl font-bold">Profile</h6>
    </div>
  </div>
    <div class="px-6">
      <div class="text-center mt-12 mb-12">
        <h3
          class="text-xl font-semibold leading-normal mb-2 text-blueGray-700 mb-2"
        >
          {{ person ? person.entity : '' }}
        </h3>
        <div class="mb-2 text-blueGray-600">
          <i class="fas fa-university mr-2 text-lg text-blueGray-400"></i>
          {{ person ? person?.label : "No known label"  }}
        </div>
      </div>
    </div>
  </div>
</template>
<script>

export default {
  props: ["person"],
};
</script>
