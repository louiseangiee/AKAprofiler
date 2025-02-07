<template>
  <div class="flex flex-wrap">
    <div class="w-full lg:w-12 px-4 pb-4">
      <Searchbar 
        @personSelected="selectPerson" 
        @cleared="selectedPerson = null"
        :people="peopleData" />
    </div>
    <div class="w-full lg:w-4/12 px-4" v-if="selectedPerson">
      <CardProfile :person="selectedPerson"/>
    </div>
    <div class="w-full lg:w-8/12 px-4" v-if="selectedPerson">
      <div
        class="relative flex flex-col min-w-0 break-words w-full shadow-lg rounded-lg border-0"
      >
        <ul class="flex flex-wrap text-sm font-medium text-center text-gray-500">
          <li class="me-2">
            <a href="#" 
              @click="activeTab = 'info'"
              class="text-blueGray-700 text-xl font-bold"
              :class="activeTab === 'info' ? activeClass : inactiveClass">
              More Information
            </a>
          </li>
          <li class="me-2">
            <a href="#" 
              class="text-blueGray-700 text-xl font-bold"
              @click="activeTab = 'graph'"
              :class="activeTab === 'graph' ? activeClass : inactiveClass">
              Network Graph
            </a>
          </li>
        </ul>
      </div>
      <!-- TABS -->
      
      <!-- TAB CONTENT -->
      <div v-if="activeTab === 'info'">
        <CardDetails :person="selectedPerson"/>
      </div>
      <div v-if="activeTab === 'graph'">
        <NetworkGraph :person="selectedPerson"/>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import CardDetails from "@/components/Cards/CardDetails.vue";
import CardProfile from "@/components/Cards/CardProfile.vue";
import Searchbar from "@/components/Search/Searchbar.vue";
import NetworkGraph from "@/components/Graphs/NetworkGraph.vue";

export default {
  components: {
    CardDetails,
    CardProfile,
    Searchbar,
    NetworkGraph,
  },
  data() {
    return {
      peopleData: [],
      selectedPerson: null,
      activeTab: "info", // Default tab is "More Information"
      activeClass: "inline-block text-blue-600 bg-white mb-0 px-6 py-6 rounded-t-lg active dark:bg-gray-800 dark:text-blue-500",
      inactiveClass: "inline-block bg-blueGray-200 mb-0 px-6 py-6 rounded-t-lg hover:text-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800 dark:hover:text-gray-300 bg-gray-100",
    };
  },
  created() {
    this.fetchPeopleData();
  },
  methods: {
    async fetchPeopleData() {
      try {
        const response = await axios.get('http://localhost:5000/entities/people');
        this.peopleData = response.data.people_entities;
      } catch (error) {
        console.error("Error fetching people data:", error);
      }
    },
    selectPerson(person) {
      this.selectedPerson = person;
      this.activeTab = "info"; // Reset to first tab when a person is selected
    },
  },
};
</script>