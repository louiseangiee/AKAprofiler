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
      <!-- <div class="flex flex-wrap justify-center">
        <div class="w-full px-4 text-center mt-5">
          <div class="flex justify-center py-4 lg:pt-4 pt-8">
            <div class="mr-4 p-3 text-center">
              <span
                class="text-xl font-bold block uppercase tracking-wide text-blueGray-600"
              >
                22
              </span>
              <span class="text-sm text-blueGray-400">Friends</span>
            </div>
            <div class="mr-4 p-3 text-center">
              <span
                class="text-xl font-bold block uppercase tracking-wide text-blueGray-600"
              >
                10
              </span>
              <span class="text-sm text-blueGray-400">Photos</span>
            </div>
            <div class="lg:mr-4 p-3 text-center">
              <span
                class="text-xl font-bold block uppercase tracking-wide text-blueGray-600"
              >
                89
              </span>
              <span class="text-sm text-blueGray-400">Comments</span>
            </div>
          </div>
        </div>
      </div> -->
      <div class="text-center mt-12 mb-12">
        <h3
          class="text-xl font-semibold leading-normal mb-2 text-blueGray-700 mb-2"
        >
          {{ person ? person.name : '' }}
        </h3>
        <div
          class="text-sm leading-normal mt-0 mb-2 text-blueGray-400 font-bold uppercase"
        >
          <i class="fas fa-map-marker-alt mr-2 text-lg text-blueGray-400"></i>
          {{ person ? person.location : "" }}
        </div>
        <div class="mb-2 text-blueGray-600">
          <i class="fas fa-university mr-2 text-lg text-blueGray-400"></i>
          {{ person ? person.organization : "" }}
        </div>
        <div class="mt-10 pt-10 border-blueGray-200 text-center">
            <div class="flex justify-center w-full">
              <button
                class="bg-emerald-500 text-white active:bg-emerald-600 font-bold uppercase text-sm px-4 py-2 rounded shadow hover:shadow-md outline-none focus:outline-none ease-linear transition-all duration-150"
                type="button"
              >
              View Correlation Graph
              </button>
          </div>
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
