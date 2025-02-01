<template>
  <div
    class="relative flex flex-col min-w-0 break-words w-full mb-6 shadow-lg rounded-lg bg-blueGray-100 border-0"
  >
    <div class="rounded-t bg-white mb-0 px-6 py-6">
      <div class="text-center flex justify-between">
        <h6 class="text-blueGray-700 text-xl font-bold">More Information</h6>
      </div>
    </div>
    <div class="flex-auto px-4 lg:px-10 py-10 pt-0">
      <form>
        <h6 class="text-blueGray-400 text-sm mt-3 mb-6 font-bold uppercase">
          Connections to Crime
        </h6>
        <div>
          <ul>
            <li v-for="crime in person.crimes" :key="crime.type">
              <b>{{ crime.type }}</b> - {{ crime.date }} at {{ crime.location }}
            </li>
          </ul>
        
        </div>

        <hr class="mt-6 border-b-1 border-blueGray-300" />

        <h6 class="text-blueGray-400 text-sm mt-3 mb-6 font-bold uppercase">
          Connections to Other Organizations
        </h6>
        <div class="flex flex-wrap">
          <p>
            <ul>
              <li>Organization Name: Organization A</li>
              <li>Connection: Partnered with James Smith</li>
              <li>Location: Los Angeles, California</li>
            </ul>
            &nbsp;
            <ul>
              <li>Organization Name: Organization B</li>
              <li>Connection: Partnered with Jenna Stones</li>
              <li>Location: Los Angeles, California</li>
            </ul>
            &nbsp;
            <ul>
              <li>Organization Name: Organization C</li>
              <li>Connection: Partnered with John Doe</li>
              <li>Location: Los Angeles, California</li>
            </ul>
          </p>
        </div>

        <hr class="mt-6 border-b-1 border-blueGray-300" />

        <h6 class="text-blueGray-400 text-sm mt-3 mb-6 font-bold uppercase">
          Other Details
        </h6>
        <div class="flex flex-wrap">
          <div class="w-full lg:w-12/12 px-4">
            <div class="relative w-full mb-3">
              <label
                class="block uppercase text-blueGray-600 text-xs font-bold mb-2"
                htmlFor="grid-password"
              >
                Additional Details on Jenna Stones
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