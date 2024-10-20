<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { invoke } from '@tauri-apps/api/core';
  import { mdiPlay, mdiPause, mdiInformation, mdiFilter } from '@mdi/js';
  import AppLayout from '../AppLayout.svelte';

  interface FirewallLog {
    rulenr?: string;
    interface?: string;
    src?: string;
    dst?: string;
    srcport?: string;
    dstport?: string;
    protoname?: string;
    action?: string;
    __timestamp__?: string;
    label?: string;
    digest?: string;
  }

  interface LogFilters {
    action: string[];
    interface_name: string[];
    dir: string[];
  }

  interface InterfaceNames {
    [key: string]: string;
  }

  let logs: FirewallLog[] = [];
  let filters: LogFilters | null = null;
  let interfaceNames: InterfaceNames | null = null;
  let isPlaying = true;
  let updateInterval: number;
  let selectedLog: FirewallLog | null = null;
  let showModal = false;
  let showFilters = false;
  let lastDigest = '';

  let selectedAction = '';
  let selectedInterface = '';
  let selectedDirection = '';
  const limit = 1000;

  let logWorker: Worker;

  function formatTimestamp(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleString();
  }

  async function fetchLogFilters() {
    try {
      filters = await invoke<LogFilters>('get_log_filters');
    } catch (error) {
      console.error('Failed to fetch log filters:', error);
    }
  }

  async function fetchInterfaceNames() {
    try {
      interfaceNames = await invoke<InterfaceNames>('get_interface_names');
    } catch (error) {
      console.error('Failed to fetch interface names:', error);
    }
  }

  async function fetchAndProcessLogs() {
    try {
      const newLogs = await invoke<FirewallLog[]>('get_firewall_logs');
      if (newLogs.length > 0) {
        lastDigest = newLogs[0].digest || '';
        logWorker.postMessage({
          type: 'processlogs',
          logs: newLogs,
          currentLogs: logs,
          filters: {
            action: selectedAction,
            interface: selectedInterface,
            direction: selectedDirection
          },
          limit
        });
      }
    } catch (error) {
      console.error('Failed to fetch logs:', error);
    }
  }

  function togglePlay() {
    isPlaying = !isPlaying;
    if (isPlaying) {
      startUpdating();
    } else {
      stopUpdating();
    }
  }

  function startUpdating() {
    updateInterval = setInterval(fetchAndProcessLogs, 1000) as unknown as number;
  }

  function stopUpdating() {
    clearInterval(updateInterval);
  }

  function showLogDetails(log: FirewallLog) {
    selectedLog = log;
    showModal = true;
  }

  function toggleFilters() {
    showFilters = !showFilters;
  }

  async function applyFilters() {
    await fetchAndProcessLogs();
    showFilters = false;
  }

  onMount(async () => {
    logWorker = new Worker(new URL('./logWorker.ts', import.meta.url), { type: 'module' });
    logWorker.onmessage = (event) => {
      if (event.data.type === 'processedlogs') {
        logs = event.data.logs;
      }
    };

    await Promise.all([fetchLogFilters(), fetchInterfaceNames()]);
    await fetchAndProcessLogs();
    startUpdating();
  });

  onDestroy(() => {
    stopUpdating();
    if (logWorker) {
      logWorker.terminate();
    }
  });
</script>

<!-- The rest of your HTML remains the same -->
<AppLayout>
  <div class="p-4">
    <h1 class="text-2xl font-bold mb-4">Live Firewall Logs</h1>
    
    <div class="mb-4 flex flex-col sm:flex-row justify-between gap-2">
      <button class="btn btn-primary" on:click={togglePlay}>
        <svg class="w-6 h-6 mr-2" viewBox="0 0 24 24">
          <path fill="currentColor" d={isPlaying ? mdiPause : mdiPlay} />
        </svg>
        {isPlaying ? 'Pause' : 'Play'}
      </button>
      <button class="btn btn-secondary" on:click={toggleFilters}>
        <svg class="w-6 h-6 mr-2" viewBox="0 0 24 24">
          <path fill="currentColor" d={mdiFilter} />
        </svg>
        Filters
      </button>
    </div>

    {#if showFilters && filters && interfaceNames}
      <div class="mb-4 p-4 bg-base-200 rounded-lg">
        <h2 class="text-lg font-semibold mb-2">Filters</h2>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <select bind:value={selectedAction} class="select select-bordered w-full">
            <option value="">Select Action</option>
            {#each filters.action as action}
              <option value={action}>{action}</option>
            {/each}
          </select>
          <select bind:value={selectedInterface} class="select select-bordered w-full">
            <option value="">Select Interface</option>
            {#each Object.entries(interfaceNames) as [key, value]}
              <option value={key}>{value}</option>
            {/each}
          </select>
          <select bind:value={selectedDirection} class="select select-bordered w-full">
            <option value="">Select Direction</option>
            {#each filters.dir as dir}
              <option value={dir}>{dir}</option>
            {/each}
          </select>
        </div>
        <button class="btn btn-primary mt-4 w-full sm:w-auto" on:click={applyFilters}>Apply Filters</button>
      </div>
    {/if}

    <!-- Mobile view -->
    <div class="lg:hidden space-y-2">
      {#each logs as log}
        <div class="card bg-base-100 shadow-sm {log.action === 'pass' ? 'border-l-4 border-success' : log.action === 'block' ? 'border-l-4 border-error' : ''}">
          <div class="card-body p-2">
            <div class="flex justify-between items-center mb-1">
              <span class="text-xs font-semibold">{log.__timestamp__ ? formatTimestamp(log.__timestamp__) : 'N/A'}</span>
              <span class="badge badge-sm {log.action === 'pass' ? 'badge-success' : log.action === 'block' ? 'badge-error' : ''}">
                {log.action || 'N/A'}
              </span>
            </div>
            <div class="grid grid-cols-2 gap-x-2 text-s">
              <p><span class="font-semibold">Interface:</span> {interfaceNames?.[log.interface || ''] || log.interface || 'N/A'}</p>
              <p><span class="font-semibold">Protocol:</span> {log.protoname || 'N/A'}</p>
              <p><span class="font-semibold">Source:</span> {log.src ? `${log.src}${log.srcport ? `:${log.srcport}` : ''}` : 'N/A'}</p>
              <p><span class="font-semibold">Destination:</span> {log.dst ? `${log.dst}${log.dstport ? `:${log.dstport}` : ''}` : 'N/A'}</p>
            </div>
            <p class="text-s mt-1"><span class="font-semibold">Label:</span> {log.label || 'N/A'}</p>
            <div class="card-actions justify-end mt-1">
              <button class="btn btn-xs btn-ghost" on:click={() => showLogDetails(log)}>
                <svg class="w-4 h-4" viewBox="0 0 24 24">
                  <path fill="currentColor" d={mdiInformation} />
                </svg>
                Details
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>

    <!-- Desktop view -->
    <div class="hidden lg:block overflow-x-auto">
      <table class="table table-compact w-full">
        <thead>
          <tr>
            <th class="py-2 text-xs">Time</th>
            <th class="py-2 text-xs">Interface</th>
            <th class="py-2 text-xs">Source</th>
            <th class="py-2 text-xs">Destination</th>
            <th class="py-2 text-xs">Protocol</th>
            <th class="py-2 text-xs">Action</th>
            <th class="py-2 text-xs">Label</th>
            <th class="py-2 text-xs">Details</th>
          </tr>
        </thead>
        <tbody>
          {#each logs as log}
            <tr class="hover:bg-base-200 {log.action === 'pass' ? 'bg-success/10' : log.action === 'block' ? 'bg-error/10' : ''}">
              <td class="py-1 text-xs">{log.__timestamp__ ? formatTimestamp(log.__timestamp__) : 'N/A'}</td>
              <td class="py-1 text-xs">{interfaceNames?.[log.interface || ''] || log.interface || 'N/A'}</td>
              <td class="py-1 text-xs">{log.src ? `${log.src}${log.srcport ? `:${log.srcport}` : ''}` : 'N/A'}</td>
              <td class="py-1 text-xs">{log.dst ? `${log.dst}${log.dstport ? `:${log.dstport}` : ''}` : 'N/A'}</td>
              <td class="py-1 text-xs">{log.protoname || 'N/A'}</td>
              <td class="py-1 text-xs">
                <span class="badge badge-sm {log.action === 'pass' ? 'badge-success' : log.action === 'block' ? 'badge-error' : ''}">
                  {log.action || 'N/A'}
                </span>
              </td>
              <td class="py-1 text-xs">{log.label || 'N/A'}</td>
              <td class="py-1 text-xs">
                <button class="btn btn-xs btn-ghost p-1" on:click={() => showLogDetails(log)}>
                  <svg class="w-3 h-3" viewBox="0 0 24 24">
                    <path fill="currentColor" d={mdiInformation} />
                  </svg>
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
    
    {#if showModal && selectedLog}
      <div class="modal modal-open">
        <div class="modal-box relative">
          <button 
            class="btn btn-sm btn-circle absolute right-2 top-2" 
            on:click={() => showModal = false}
          >
            ✕
          </button>
          <h3 class="font-bold text-lg pr-8">Log Details</h3>
          <div class="mt-4 max-h-[70vh] overflow-y-auto">
            <pre class="whitespace-pre-wrap break-words">{JSON.stringify(selectedLog, null, 2)}</pre>
          </div>
        </div>
      </div>
    {/if}
  </div>
</AppLayout>