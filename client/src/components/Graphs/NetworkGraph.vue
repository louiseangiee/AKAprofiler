<template>
  <div class="relative flex flex-col min-w-0 break-words w-full mb-6 shadow-lg rounded-b-lg bg-blueGray-100 border-0">
    <h1 class="text-2xl font-bold text-blue-600 mt-4 mb-4 text-center">Network Graph</h1>
    <!-- Graph Container -->
    <div ref="graphContainer" class="w-full h-[500px] border bg-white shadow-lg rounded-lg"></div>
  </div>
</template>

<script>
import * as d3 from "d3";

export default {
  props: ["person"],
  mounted() {
    this.createGraph();
  },
  watch: {
    person: {
      immediate: true,
      handler(newPerson) {
        if (newPerson) {
          this.$nextTick(() => this.createGraph());
        }
      }
    }
  },
  methods: {
    async createGraph() {
  if (!this.person || !this.person.entity) {
    console.error("Person data is missing or invalid!");
    return;
  }

  const container = this.$refs.graphContainer;
  if (!container) {
    console.error("Graph container not found!");
    return;
  }

  // Clear previous graph
  container.innerHTML = "";

  try {
    // Fetch relationships for the selected entity
    const response = await fetch(`http://localhost:5000/relationships/entity/${encodeURIComponent(this.person.entity)}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch relationships for entity: ${this.person.entity}`);
    }
    const data = await response.json();
    console.log("Fetched Relationships:", data);

    if (!data.relationships || data.relationships.length === 0) {
      console.warn(`No relationships found for entity: ${this.person.entity}`);
      return;
    }

    // Prepare graph data
    const nodesMap = new Map();
    const links = [];

    // Add the main entity as a node
    nodesMap.set(this.person.entity, { id: this.person.entity, type: this.person.label || "ORG", group: 1 });

    // Process relationships to create nodes and links
    data.relationships.forEach((relationship) => {
      // Add entity_1 as a node
      if (!nodesMap.has(relationship.entity_1_name)) {
        nodesMap.set(relationship.entity_1_name, { id: relationship.entity_1_name, type: relationship.entity_1_type, group: 2 });
      }

      // Add entity_2 as a node
      if (!nodesMap.has(relationship.entity_2_name)) {
        nodesMap.set(relationship.entity_2_name, { id: relationship.entity_2_name, type: relationship.entity_2_type, group: 3 });
      }

      // Add the relationship as a link
      links.push({
        source: relationship.entity_1_name,
        target: relationship.entity_2_name,
        relation: relationship.relationship
      });
    });

    // Convert nodesMap to an array
    const nodes = Array.from(nodesMap.values());
    console.log("Nodes:", nodes);
    console.log("Links:", links);

    // Render the graph
    this.renderGraph(container, nodes, links);
  } catch (error) {
    console.error("Error creating graph:", error);
  }
},

renderGraph(container, nodes, links) {
  const width = container.clientWidth || 800;
  const height = container.clientHeight || 500;

  // Create SVG and enable zoom behavior
  const svg = d3.select(container)
    .append("svg")
    .attr("width", "100%")
    .attr("height", "100%")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("preserveAspectRatio", "xMidYMid meet")
    .call(
      d3.zoom()
        .scaleExtent([0.5, 2])
        .on("zoom", (event) => g.attr("transform", event.transform))
    );

  const g = svg.append("g");

  // D3 Force Simulation
  const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(150))
    .force("charge", d3.forceManyBody().strength(-400))
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
    .attr("font-size", "12px")
    .attr("fill", "black")
    .attr("text-anchor", "middle")
    .text(d => d.relation);

  // Create Nodes
  const node = g.selectAll(".node")
    .data(nodes)
    .enter()
    .append("circle")
    .attr("r", 14)
    .attr("fill", d => {
      if (d.type === "Person") return "red";
      if (d.type === "ORG") return "gold";
      return "green";
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

  // Add Labels to Nodes
  const nodeLabels = g.selectAll(".node-label")
    .data(nodes)
    .enter()
    .append("text")
    .attr("font-size", "14px")
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

    node.attr("cx", d => d.x).attr("cy", d => d.y);
    nodeLabels.attr("x", d => d.x).attr("y", d => d.y);
  });
}
  }
};
</script>

<style scoped>
.text-label, .link-label {
  font-family: Arial, sans-serif;
  font-size: 12px;
  fill: black;
}
</style>