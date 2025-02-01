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
      <CardDetails :person="selectedPerson"/>
    </div>
  </div>
</template>

<script>
import CardDetails from "@/components/Cards/CardDetails.vue";
import CardProfile from "@/components/Cards/CardProfile.vue";
import Searchbar from "@/components/Search/Searchbar.vue";

export default {
  components: {
    CardDetails,
    CardProfile,
    Searchbar,
  },
  data() {
    return {
      peopleData: [
        {
          id: 1,
          name: "Jenna Stones",
          location: "Los Angeles, California",
          organization: "XYZ Corporation",
          crimes: [
            { type: "Robbery", date: "12/12/2021", location: "Convenience Store" },
          ],
        },
        {
          id: 2,
          name: "James Smith",
          location: "New York, USA",
          organization: "ABC Corp",
          crimes: [{ type: "Fraud", date: "01/05/2022", location: "Online Scam" }],
        },
      ],
      selectedPerson: null,
    };
  },
  methods: {
    selectPerson(person) {
      this.selectedPerson = person;
    },
  },
};
</script>
