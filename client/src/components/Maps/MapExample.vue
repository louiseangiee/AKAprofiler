<template>
  <div class="flex flex-col items-center justify-center h-screen bg-gray-100">
    <h1 class="text-2xl font-bold text-blue-600 mt-4 mb-4">Network Graph</h1>
    <div ref="graphContainer" class="w-full h-full border bg-white shadow-lg rounded-lg"></div>
  </div>
</template>

<script>
import * as d3 from "d3";

export default {
  mounted() {
    this.createGraph();
  },
  methods: {
    createGraph() {
      console.log("Graph container found:", this.$refs.graphContainer);
      console.log("Graph data:", data);
      const container = this.$refs.graphContainer;
      if (!container) {
        console.error("Container not found!");
        return;
      }

      container.innerHTML = ""; // Clear previous graph if it exists

      // Get the correct width & height
      const width = window.innerWidth * 0.78321; 
      const height = window.innerHeight * 0.8; 

      console.log("Graph container dimensions:", width, height);

      // Create SVG
      const svg = d3.select(container)
        .append("svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("viewBox", `0 0 ${width} ${height}`)  // Ensures everything fits
        .attr("preserveAspectRatio", "xMidYMid meet")
        .call(d3.zoom().on("zoom", (event) => {  // Enable zoom and pan
          g.attr("transform", event.transform);
        }));

      const g = svg.append("g"); // Create group for zooming

      // Mock Data
      const data = {
        nodes: [
          // PEOPLE
          { id: "Jenna Stones", type: "Person", group: 1 },
          { id: "James Smith", type: "Person", group: 1 },
          { id: "Alice Johnson", type: "Person", group: 1 },
          { id: "Robert White", type: "Person", group: 1 },

          // JOBS
          { id: "Software Engineer", type: "Job", group: 2 },
          { id: "CEO", type: "Job", group: 2 },
          { id: "Accountant", type: "Job", group: 2 },

          // CRIMES
          { id: "Fraud", type: "Crime", group: 3 },
          { id: "Robbery", type: "Crime", group: 3 },
          { id: "Bribery", type: "Crime", group: 3 },
          { id: "Money Laundering", type: "Crime", group: 3 },

          // LOCATIONS
          { id: "New York", type: "Location", group: 4 },
          { id: "Los Angeles", type: "Location", group: 4 },
          { id: "Chicago", type: "Location", group: 4 },
          { id: "Miami", type: "Location", group: 4 }
        ],
        links: [
          // Job relationships
          { source: "Jenna Stones", target: "Software Engineer", relation: "works as" },
          { source: "James Smith", target: "CEO", relation: "works as" },
          { source: "Alice Johnson", target: "Accountant", relation: "works as" },
          { source: "Robert White", target: "CEO", relation: "works as" },

          // Crimes
          { source: "Jenna Stones", target: "Fraud", relation: "committed" },
          { source: "James Smith", target: "Robbery", relation: "committed" },
          { source: "Alice Johnson", target: "Bribery", relation: "committed" },
          { source: "Robert White", target: "Money Laundering", relation: "committed" },

          // Crime Locations
          { source: "Fraud", target: "New York", relation: "crime location" },
          { source: "Money Laundering", target: "Los Angeles", relation: "crime location" },
          { source: "Bribery", target: "Chicago", relation: "crime location" },
          { source: "Money Laundering", target: "Miami", relation: "crime location" },

          // Partnerships in crime
          { source: "Jenna Stones", target: "James Smith", relation: "partnered with" },
          { source: "James Smith", target: "Alice Johnson", relation: "partnered with" },
          { source: "Alice Johnson", target: "Robert White", relation: "partnered with" },
          { source: "Robert White", target: "Jenna Stones", relation: "partnered with" }
        ]
      };


      console.log("Graph data:", data);  // **Now it should print correctly**

      // Force Simulation
      const simulation = d3.forceSimulation(data.nodes)
        .force("link", d3.forceLink(data.links).id(d => d.id).distance(200)) // Increase distance
        .force("charge", d3.forceManyBody().strength(-500)) // Spread out nodes
        .force("center", d3.forceCenter(width / 2, height / 2));

      // Create Links
      const link = g.selectAll(".link")
        .data(data.links)
        .enter()
        .append("line")
        .attr("stroke", "#aaa")
        .attr("stroke-width", 2);

      // Create Relationship Labels
      const linkLabels = g.selectAll(".link-label")
        .data(data.links)
        .enter()
        .append("text")
        .attr("class", "link-label")
        .attr("font-size", "12px")
        .attr("fill", "black")
        .attr("text-anchor", "middle")
        .text(d => d.relation);

      // Create Nodes
      const node = g.selectAll(".node")
        .data(data.nodes)
        .enter()
        .append("circle")
        .attr("r", 12)
        .attr("fill", d => {
          if (d.type === "Person") return "red";
          if (d.type === "Job") return "blue";
          if (d.type === "Crime") return "gold";
          if (d.type === "Location") return "green";
          return "gray";
        })
        .call(
          d3.drag()
            .on("start", (event, d) => {
              if (!event.active) simulation.alphaTarget(0.3).restart();
              d.fx = d.x;
              d.fy = d.y;
            })
            .on("drag", (event, d) => {
              d.fx = event.x;
              d.fy = event.y;
            })
            .on("end", (event, d) => {
              if (!event.active) simulation.alphaTarget(0);
              d.fx = null;
              d.fy = null;
            })
        );

      // Add Node Labels
      const nodeLabels = g.selectAll(".node-label")
        .data(data.nodes)
        .enter()
        .append("text")
        .attr("class", "node-label")
        .attr("font-size", "12px")
        .attr("text-anchor", "middle")
        .attr("dy", -18)
        .text(d => d.id);

      // Update positions during simulation
      simulation.on("tick", () => {
        link
          .attr("x1", d => d.source.x)
          .attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x)
          .attr("y2", d => d.target.y);

        linkLabels
          .attr("x", d => (d.source.x + d.target.x) / 2)
          .attr("y", d => (d.source.y + d.target.y) / 2);

        node
          .attr("cx", d => d.x)
          .attr("cy", d => d.y);

        nodeLabels
          .attr("x", d => d.x)
          .attr("y", d => d.y);
      });
    }
  }
};
</script>

<style scoped>
h1 {
  font-family: Arial, sans-serif;
}
</style>
