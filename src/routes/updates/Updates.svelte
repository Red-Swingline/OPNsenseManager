<script lang="ts">
  import { onMount } from 'svelte';
  import { invoke } from "@tauri-apps/api/core";
  import { toasts } from '$lib/stores/toastStore';
  import { mdiRefresh } from '@mdi/js';

  interface FirmwareStatus {
    product_id: string;
    product_version: string;
    product: {
      product_arch: string;
      product_hash: string;
      product_mirror: string;
      product_repos: string;
      product_time: string;
    };
    last_check: string;
  }

  let firmwareStatus: FirmwareStatus | null = null;
  let isChecking = false;

  onMount(async () => {
    await getCurrentStatus();
  });

  async function getCurrentStatus() {
    try {
      firmwareStatus = await invoke<FirmwareStatus>('get_current_firmware_status');
    } catch (error) {
      console.error('Failed to get current firmware status:', error);
      toasts.error('Failed to get current firmware status. Please try again.');
    }
  }

  async function checkForUpdates() {
    isChecking = true;
    try {
      firmwareStatus = await invoke<FirmwareStatus>('check_for_updates');
      toasts.success('Update check completed successfully.');
    } catch (error) {
      console.error('Failed to check for updates:', error);
      toasts.error('Failed to check for updates. Please try again.');
    } finally {
      isChecking = false;
    }
  }
</script>

<div class="p-4 max-w-3xl mx-auto">
  <h2 class="text-2xl font-bold mb-4">Firmware Status</h2>

  {#if firmwareStatus}
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <table class="table w-full">
          <tbody>
            <tr>
              <td class="font-semibold">Type</td>
              <td>{firmwareStatus.product_id}</td>
            </tr>
            <tr>
              <td class="font-semibold">Version</td>
              <td>{firmwareStatus.product_version}</td>
            </tr>
            <tr>
              <td class="font-semibold">Architecture</td>
              <td>{firmwareStatus.product.product_arch}</td>
            </tr>
            <tr>
              <td class="font-semibold">Commit</td>
              <td>{firmwareStatus.product.product_hash}</td>
            </tr>
            <tr>
              <td class="font-semibold">Mirror</td>
              <td>
                <a href={firmwareStatus.product.product_mirror} class="link link-primary" target="_blank" rel="noopener noreferrer">
                  {firmwareStatus.product.product_mirror}
                </a>
              </td>
            </tr>
            <tr>
              <td class="font-semibold">Repositories</td>
              <td>{firmwareStatus.product.product_repos}</td>
            </tr>
            <tr>
              <td class="font-semibold">Updated on</td>
              <td>{firmwareStatus.product.product_time}</td>
            </tr>
            <tr>
              <td class="font-semibold">Checked on</td>
              <td>{firmwareStatus.last_check}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  {:else}
    <p class="mb-6">Loading current status...</p>
  {/if}

  <button
    class="btn btn-primary"
    on:click={checkForUpdates}
    disabled={isChecking}
  >
    {#if isChecking}
      <span class="loading loading-spinner"></span>
    {:else}
      <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
        <path fill="currentColor" d={mdiRefresh} />
      </svg>
    {/if}
    Check for Updates
  </button>

  {#if isChecking}
    <p class="mt-4">Checking for updates... This may take a few moments.</p>
  {/if}
</div>