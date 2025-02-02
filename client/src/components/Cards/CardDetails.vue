<template>
  <div
    class="relative flex flex-col min-w-0 break-words w-full mb-6 shadow-lg rounded-b-lg bg-blueGray-100 border-0"
  >
    <div class="flex-auto px-4 lg:px-10 py-10 pt-0">
      <form>
        <h6 class="text-blueGray-400 text-sm mt-3 mb-6 font-bold uppercase">
          Connections to Crime
        </h6>
        <div v-if="person.crimes && person.crimes.length > 0">
          <ul>
            <li v-for="crime in person.crimes" :key="crime.type">
              <b>{{ crime.type }}</b> - {{ crime.date }} at {{ crime.location }}
            </li>
          </ul>
        </div>
        <div v-else>
          <p class="text-gray-500">No known crime connections.</p>
        </div>
        <hr class="mt-6 border-b-1 border-blueGray-300" />
        <h6 class="text-blueGray-400 text-sm mt-3 mb-6 font-bold uppercase">
          Connections to Other People
        </h6>
        <div v-if="person.partners && person.partners.length > 0">
          <ul>
            <li v-for="partner in person.partners" :key="partner">
              <b>{{ partner }}</b> - Partner in crime
            </li>
          </ul>
        </div>
        <div v-else>
          <p class="text-gray-500">No known connections to other people.</p>
        </div>


        <hr class="mt-6 border-b-1 border-blueGray-300" />

        <h6 class="text-blueGray-400 text-sm mt-3 mb-6 font-bold uppercase">
          Notes
        </h6>
        <div class="flex flex-wrap">
          <div class="w-full lg:w-12/12 px-4">
            <div class="relative w-full mb-3">
              <label
                class="block uppercase text-blueGray-600 text-xs font-bold mb-2"
                htmlFor="grid-password"
              >
                Additional Details on {{ person ? person.name : "Unknown" }}
              </label>
              <textarea
                type="text"
                class="border-0 px-3 py-3 placeholder-blueGray-300 text-blueGray-600 bg-white rounded text-sm shadow focus:outline-none focus:ring w-full ease-linear transition-all duration-150"
                rows="4"
              >
                    Insert your own notes here
                  </textarea>
            </div>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  props: ["person"],
};
</script>