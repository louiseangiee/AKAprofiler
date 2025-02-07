<template>
  <div class="relative flex w-full flex-wrap items-stretch">
    <span
      class="z-10 h-full leading-snug font-normal absolute text-center text-blueGray-300 absolute bg-transparent rounded text-base items-center justify-center w-8 pl-3 py-5"
    >
      <i class="fas fa-search"></i>
    </span>
    <input
      type="text"
      v-model="searchQuery"
      @input="filterPeople"
      placeholder="Search here..."
      class="border-0 px-3 py-5 placeholder-blueGray-300 text-blueGray-600 relative bg-white bg-white rounded text-ml shadow outline-none focus:outline-none focus:ring w-full pl-10"
    />
    <transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0 translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-1"
    >
      <ul
        v-show="searchQuery.trim() && filteredPeople.length > 0"
        class="absolute z-50 w-full mt-20 bg-white border border-blueGray-100 rounded shadow max-h-48 overflow-y-auto top-full"
        style="max-height: 200px; overflow-y: auto;"
      >
        <li
          v-for="person in filteredPeople"
          :key="person.id"
          @click="selectPerson(person)"
          class="cursor-pointer px-4 py-4 text-blueGray-700 hover:bg-blueGray-50"
        >
          {{ person.entity }}
        </li>
      </ul>
    </transition>
  </div>
</template>

<script>
export default {
  props: {
    people: {
      type: Array,
      required: true,
      default: () => [], // Default to an empty array if no data is provided
    },
  },
  data() {
    return {
      searchQuery: "",
      filteredPeople: [],
    };
  },
  methods: {
    filterPeople() {
      // Ensure `this.people` is an array and each item has a `name` property
      this.filteredPeople = (this.people || []).filter((person) => {
        if (!person || typeof person.entity !== "string") {
          console.warn("Invalid person object:", person);
          return false;
        }
        return person.entity.toLowerCase().includes(this.searchQuery.toLowerCase());
      });
    },
    selectPerson(person) {
      this.$emit("personSelected", person); // Pass selected person to parent
      this.searchQuery = person.entity; // Show selected name
      this.filteredPeople = []; // Hide dropdown
    },
  },
  watch: {
    searchQuery(newValue) {
      if (!newValue) {
        this.$emit("cleared"); // Let the parent know the search has been cleared
      }
    },
  },
};
</script>

<style scoped>
/* Ensures dropdown stays visible */
ul {
  max-height: 200px;
  overflow-y: auto;
}
</style>