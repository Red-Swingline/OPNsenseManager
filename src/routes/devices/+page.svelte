<script lang="ts">
  import { onMount } from 'svelte';
  import { invoke } from "@tauri-apps/api/core";
  import { fade, fly } from 'svelte/transition';
  import AppLayout from '../AppLayout.svelte';
  import { toasts } from '$lib/stores/toastStore';
  import { authStore } from '$lib/stores/authStore';
  import { fabStore, toggleFab, closeFab } from '$lib/stores/fabStore';
  import { mdiRefresh, mdiDelete, mdiDotsVertical, mdiClose, mdiMagnify } from '@mdi/js';

  let devices = [];
  let filteredDevices = [];
  let isLoading = true;
  let selectedDevice = null;
  let isModalOpen = false;
  let vendorInfo = "";

  let filters = {
    ip: '',
    hostname: ''
  };

  const columns = [
    { key: 'ip', title: 'IP Address' },
    { key: 'hostname', title: 'Hostname' }
  ];

  onMount(async () => {
    if ($authStore.isLoggedIn) {
      await fetchDevices();
    }
  });

  async function fetchDevices() {
    isLoading = true;
    try {
      devices = await invoke("get_devices");
      applyFilters();
      toasts.success("Devices fetched successfully");
    } catch (error) {
      console.error("Failed to fetch devices:", error);
      toasts.error("Failed to fetch devices. Please try again.");
    } finally {
      isLoading = false;
    }
  }

  function applyFilters() {
    filteredDevices = devices.filter(device =>
      Object.keys(filters).every(key =>
        String(device[key] || '').toLowerCase().includes(filters[key].toLowerCase())
      )
    );
  }

  async function handleFlushArpTable() {
    try {
      await invoke("flush_arp_table");
      toasts.success("ARP table flushed successfully");
      await fetchDevices();
    } catch (error) {
      console.error("Failed to flush ARP table:", error);
      toasts.error("Failed to flush ARP table. Please try again.");
    }
  }

  async function openModal(device) {
    selectedDevice = device;
    isModalOpen = true;
    try {
      vendorInfo = await invoke("get_vendor_info", { mac: device.mac });
    } catch (error) {
      console.error("Failed to fetch vendor info:", error);
      vendorInfo = "Unknown";
    }
  }

  function closeModal() {
    isModalOpen = false;
    selectedDevice = null;
    vendorInfo = "";
  }

  function handleOutsideClick(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest('.fab-container')) {
      closeFab();
    }
  }

  async function fetchDevicesAndCloseFab() {
    await fetchDevices();
    closeFab();
  }

  async function handleFlushArpTableAndCloseFab() {
    await handleFlushArpTable();
    closeFab();
  }

  $: {
    filters;
    if (devices.length > 0) {
      applyFilters();
    }
  }
</script>

<svelte:window on:click={handleOutsideClick} />

<AppLayout>
  <div class="max-w-6xl mx-auto">
    <h2 class="text-2xl font-bold mb-6">Devices</h2>
    
    {#if isLoading}
      <div class="text-center">
        <span class="loading loading-spinner loading-lg"></span>
        <p class="mt-4 text-base-content">Loading devices...</p>
      </div>
    {:else if filteredDevices.length === 0}
      <p class="text-base-content">No devices found.</p>
    {:else}
      <div class="overflow-x-auto bg-base-100 rounded-lg shadow">
        <table class="table w-full">
          <thead>
            <tr>
              {#each columns as column}
                <th>
                  <div class="font-bold text-lg mb-2">{column.title}</div>
                  <div class="flex items-center bg-base-200 rounded-md px-3 py-2">
                    <svg class="w-5 h-5 mr-2 text-base-content opacity-70" viewBox="0 0 24 24">
                      <path fill="currentColor" d={mdiMagnify} />
                    </svg>
                    <input
                      type="text"
                      placeholder={`Filter ${column.title}`}
                      class="bg-transparent border-none focus:outline-none text-sm w-full"
                      bind:value={filters[column.key]}
                    />
                  </div>
                </th>
              {/each}
            </tr>
          </thead>
          <tbody>
            {#each filteredDevices as device}
              <tr class="hover:bg-base-200 transition-colors duration-200 cursor-pointer" on:click={() => openModal(device)}>
                {#each columns as column}
                  <td class="py-4">{device[column.key] || 'N/A'}</td>
                {/each}
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>

  <!-- Floating Action Button -->
  <div class="fixed bottom-6 right-6 fab-container">
    <div class="relative">
      {#if $fabStore.isExpanded}
        <div transition:fade="{{ duration: 200 }}">
          <button
            on:click={fetchDevicesAndCloseFab}
            class="fab-option btn btn-circle btn-primary absolute bottom-24 right-0"
            title="Refresh Devices"
            transition:fly="{{ y: 20, duration: 200 }}"
          >
            <svg class="w-6 h-6" viewBox="0 0 24 24">
              <path fill="currentColor" d={mdiRefresh} />
            </svg>
          </button>
          <button
            on:click={handleFlushArpTableAndCloseFab}
            class="fab-option btn btn-circle btn-secondary absolute bottom-44 right-0"
            title="Flush ARP Table"
            transition:fly="{{ y: 20, duration: 200, delay: 50 }}"
          >
            <svg class="w-6 h-6" viewBox="0 0 24 24">
              <path fill="currentColor" d={mdiDelete} />
            </svg>
          </button>
        </div>
      {/if}
      <button
        on:click={(e) => { e.stopPropagation(); toggleFab(); }}
        class="btn btn-circle btn-lg btn-primary shadow-lg"
      >
        <svg class="w-6 h-6" viewBox="0 0 24 24">
          <path fill="currentColor" d={$fabStore.isExpanded ? mdiClose : mdiDotsVertical} />
        </svg>
      </button>
    </div>
  </div>

  <!-- Modal -->
  {#if isModalOpen && selectedDevice}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-base-100 p-6 rounded-lg max-w-md w-full">
        <h3 class="text-lg font-bold mb-4">Device Details</h3>
        <p><strong>IP Address:</strong> {selectedDevice.ip}</p>
        <p><strong>Hostname:</strong> {selectedDevice.hostname}</p>
        <p><strong>MAC Address:</strong> {selectedDevice.mac}</p>
        <p><strong>Interface:</strong> {selectedDevice.intf}</p>
        <p><strong>Vendor:</strong> {vendorInfo}</p>
        <div class="mt-6 flex justify-end">
          <button class="btn btn-primary" on:click={closeModal}>Close</button>
        </div>
      </div>
    </div>
  {/if}
</AppLayout>

<style>
  .btn-circle {
    @apply rounded-full w-14 h-14 p-0 grid place-items-center;
  }
  
  .btn-lg {
    @apply w-16 h-16;
  }

  .fab-option {
    @apply w-12 h-12;
  }
</style>