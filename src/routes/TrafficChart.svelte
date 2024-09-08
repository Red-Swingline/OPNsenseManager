<script lang="ts">
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  
  export let data: { timestamp: Date; [key: string]: number }[] = [];
  export let height = 300;
  export let width = 800;
  
  let chartSvg: SVGSVGElement;
  
  $: interfaceNames = Object.keys(data[0] || {}).filter(key => key !== 'timestamp');
  
  const margin = { top: 20, right: 20, bottom: 30, left: 50 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;
  
  onMount(() => {
    const svg = d3.select(chartSvg);
  
    const x = d3.scaleTime()
      .range([0, chartWidth])
      .domain(d3.extent(data, d => new Date(d.timestamp)));
  
    const y = d3.scaleLinear()
      .range([chartHeight, 0])
      .domain([0, d3.max(data, d => {
        let sum = 0;
        interfaceNames.forEach(name => sum += d[name]);
        return sum;
      })]);
  
    const color = d3.scaleOrdinal(d3.schemeCategory10);
  
    const area = d3.area<any>()
      .x(d => x(new Date(d.data.timestamp)))
      .y0(d => y(d[0]))
      .y1(d => y(d[1]));
  
    const stack = d3.stack()
      .keys(interfaceNames)
      .order(d3.stackOrderNone)
      .offset(d3.stackOffsetNone);
  
    const series = stack(data);
  
    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);
  
    g.selectAll('.area')
      .data(series)
      .enter().append('path')
      .attr('class', 'area')
      .style('fill', (d, i) => color(i.toString()))
      .attr('d', area);
  
    // Add X axis
    g.append('g')
      .attr('transform', `translate(0,${chartHeight})`)
      .call(d3.axisBottom(x).ticks(5));
  
    // Add Y axis
    g.append('g')
      .call(d3.axisLeft(y).ticks(5))
      .append('text')
      .attr('fill', '#000')
      .attr('transform', 'rotate(-90)')
      .attr('y', 6)
      .attr('dy', '0.71em')
      .attr('text-anchor', 'end')
      .text('Traffic (Mbps)');
  
    // Add legend
    const legend = svg.append('g')
      .attr('font-family', 'sans-serif')
      .attr('font-size', 10)
      .attr('text-anchor', 'end')
      .selectAll('g')
      .data(interfaceNames.slice().reverse())
      .enter().append('g')
      .attr('transform', (d, i) => `translate(0,${i * 20})`);
  
    legend.append('rect')
      .attr('x', width - 19)
      .attr('width', 19)
      .attr('height', 19)
      .attr('fill', (d, i) => color((interfaceNames.length - 1 - i).toString()));
  
    legend.append('text')
      .attr('x', width - 24)
      .attr('y', 9.5)
      .attr('dy', '0.32em')
      .text(d => d);
  });
  </script>
  
  <div class="chart-container">
    <svg bind:this={chartSvg} {width} {height}></svg>
  </div>
  
  <style>
  .chart-container {
    width: 100%;
    margin-bottom: 20px;
  }
  
  .area {
    opacity: 0.7;
  }
  
  .area:hover {
    opacity: 0.9;
  }
  </style>