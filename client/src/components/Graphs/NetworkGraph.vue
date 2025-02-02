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
      createGraph() {
        if (!this.person || !this.person.name) {
          console.error("Person data is missing!");
          return;
        }
        console.log("Graph Data:", this.person);
  
        const container = this.$refs.graphContainer;
        if (!container) {
          console.error("Graph container not found!");
          return;
        }
        console.log("Graph container found:", container);
  
        container.innerHTML = ""; // Clear previous graph
  
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
                .scaleExtent([0.5, 2]) // Zoom limits (min, max)
                .on("zoom", (event) => g.attr("transform", event.transform))
            );

        const g = svg.append("g"); // Group for elements

        // Graph Data
        const data = {
            nodes: [
            { id: this.person.name, type: "Person", group: 1 },
            ...this.person.partners.map(name => ({ id: name, type: "Person", group: 1 })),
            ...this.person.crimes.map(crime => ({ id: crime.type, type: "Crime", group: 2 })),
            ...this.person.crimes.map(crime => ({ id: crime.location, type: "Location", group: 3 })),
            ],
            links: [
            ...this.person.partners.map(name => ({ source: this.person.name, target: name, relation: "partnered with" })),
            ...this.person.crimes.map(crime => ({ source: this.person.name, target: crime.type, relation: "committed" })),
            ...this.person.crimes.map(crime => ({ source: crime.type, target: crime.location, relation: "crime location" })),
            ]
        };

        console.log("Nodes:", data.nodes);
        console.log("Links:", data.links);

        // D3 Force Simulation
        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(150))
            .force("charge", d3.forceManyBody().strength(-400))
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
            .attr("font-size", "12px")
            .attr("fill", "black")
            .attr("text-anchor", "middle")
            .text(d => d.relation);

        // Create Nodes
        const node = g.selectAll(".node")
            .data(data.nodes)
            .enter()
            .append("circle")
            .attr("r", 14)
            .attr("fill", d => (d.type === "Person" ? "red" : d.type === "Crime" ? "gold" : "green"))
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
            .data(data.nodes)
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
  