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
    async createGraph() {
      console.log("Graph container found:", this.$refs.graphContainer);

      // Fetch relationships from the API
      const response = await fetch("http://localhost:5000/relationships");
      const { relationships } = await response.json();

      console.log("Fetched relationships:", relationships);

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
        .attr("viewBox", `0 0 ${width} ${height}`)
        .attr("preserveAspectRatio", "xMidYMid meet")
        .call(d3.zoom().on("zoom", (event) => {
          g.attr("transform", event.transform);
        }));

      const g = svg.append("g"); // Create group for zooming

      // Process the relationships into nodes and links
      const nodesMap = new Map();
      const links = [];

      relationships.forEach(rel => {
        // Add entity 1 to nodes if not already present
        if (!nodesMap.has(rel.entity_1_name)) {
          nodesMap.set(rel.entity_1_name, { id: rel.entity_1_name, type: rel.entity_1_type });
        }

        // Add entity 2 to nodes if not already present
        if (!nodesMap.has(rel.entity_2_name)) {
          nodesMap.set(rel.entity_2_name, { id: rel.entity_2_name, type: rel.entity_2_type });
        }

        // Add the relationship as a link
        links.push({
          source: rel.entity_1_name,
          target: rel.entity_2_name,
          relation: rel.relationship
        });
      });

      const nodes = Array.from(nodesMap.values());

      console.log("Processed nodes:", nodes);
      console.log("Processed links:", links);

      // Force Simulation
      const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id).distance(200))
        .force("charge", d3.forceManyBody().strength(-500))
        .force("center", d3.forceCenter(width / 2, height / 2));

      // Create Links
      const link = g.selectAll(".link")
        .data(links)
        .enter()
        .append("line")
        .attr("stroke", "#aaa")
        .attr("stroke-width", 2);

      // Create Relationship Labels
      const linkLabels = g.selectAll(".link-label")
        .data(links)
        .enter()
        .append("text")
        .attr("class", "link-label")
        .attr("font-size", "12px")
        .attr("fill", "black")
        .attr("text-anchor", "middle")
        .text(d => d.relation);

      // Create Nodes
      const node = g.selectAll(".node")
        .data(nodes)
        .enter()
        .append("circle")
        .attr("r", 12)
        .attr("fill", d => {
          if (d.type === "ORG") return "blue"; // Organizations
          return "gray"; // Default color
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
        .data(nodes)
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