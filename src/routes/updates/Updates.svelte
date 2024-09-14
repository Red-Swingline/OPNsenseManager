<script lang="ts">
  import { onMount } from 'svelte';
  import { invoke } from "@tauri-apps/api/core";
  import { toasts } from '$lib/stores/toastStore';
  import { mdiRefresh, mdiPackageVariant, mdiCog } from '@mdi/js';

  let firmwareStatus: any = null;
  let isChecking = false;
  let isUpdating = false;
  let showChangelogButton = false;
  let showUpgradeButton = false;
  let changelog = '';
  let showChangelog = false;

  onMount(async () => {
    await getFirmwareStatus();
  });

  async function getFirmwareStatus() {
    try {
      firmwareStatus = await invoke<any>('get_current_firmware_status');
      console.log('Current firmware status:', firmwareStatus);
    } catch (error) {
      console.error('Failed to get current firmware status:', error);
      toasts.error('Failed to get current firmware status. Please try again.');
    }
  }

  async function checkForUpdates() {
    isChecking = true;
    showChangelogButton = false;
    showUpgradeButton = false;
    try {
      const result = await invoke<any>('check_for_updates');
      console.log('Check for updates result:', result);
      if (result.status === "update") {
        showChangelogButton = true;
        showUpgradeButton = true;
        toasts.success('Updates are available.');
      } else {
        toasts.success('Your system is up to date.');
      }
      firmwareStatus = result;
    } catch (error) {
      console.error('Failed to check for updates:', error);
      toasts.error(`Failed to check for updates: ${error}`);
    } finally {
      isChecking = false;
    }
  }

  async function getChangelog() {
    if (firmwareStatus?.latest_version) {
      try {
        changelog = await invoke<string>('get_changelog', { version: firmwareStatus.latest_version });
        showChangelog = true;
      } catch (error) {
        console.error('Failed to get changelog:', error);
        toasts.error('Failed to get changelog. Please try again.');
      }
    }
  }

  async function startUpdate() {
    isUpdating = true;
    try {
      const result = await invoke<string>('start_update');
      console.log('Update result:', result);
      toasts.success(result);
      showChangelogButton = false;
      showUpgradeButton = false;
      await getFirmwareStatus();
    } catch (error) {
      console.error('Failed to start update:', error);
      toasts.error(`Failed to start update: ${error}`);
    } finally {
      isUpdating = false;
    }
  }
</script>

<div class="p-4 max-w-3xl mx-auto">
  <h2 class="text-2xl font-bold mb-4">Firmware Status</h2>

  {#if firmwareStatus}
    <div class="card bg-base-100 shadow-xl mb-6 overflow-x-auto">
      <div class="card-body p-4">
        <table class="table w-full">
          <tbody>
            <tr>
              <td class="font-semibold whitespace-nowrap">Version</td>
              <td class="break-all">{firmwareStatus.product_version ?? 'Unknown'}</td>
            </tr>
            <tr>
              <td class="font-semibold whitespace-nowrap">Architecture</td>
              <td class="break-all">{firmwareStatus.product?.product_arch ?? 'Unknown'}</td>
            </tr>
            <tr>
              <td class="font-semibold whitespace-nowrap">Commit</td>
              <td class="break-all">{firmwareStatus.product?.product_hash ?? 'Unknown'}</td>
            </tr>
            <tr>
              <td class="font-semibold whitespace-nowrap">Mirror</td>
              <td class="break-all">{firmwareStatus.product?.product_mirror ?? 'Unknown'}</td>
            </tr>
            <tr>
              <td class="font-semibold whitespace-nowrap">Repositories</td>
              <td class="break-all">{firmwareStatus.product?.product_repos ?? 'Unknown'}</td>
            </tr>
            <tr>
              <td class="font-semibold whitespace-nowrap">Updated on</td>
              <td class="break-all">{firmwareStatus.product?.product_time ?? 'Unknown'}</td>
            </tr>
            <tr>
              <td class="font-semibold whitespace-nowrap">Checked on</td>
              <td class="break-all">{firmwareStatus.last_check ?? 'N/A'}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  {:else}
    <p class="mb-6">Loading current status...</p>
  {/if}

  <div class="flex flex-wrap gap-4">
    <button
      class="btn btn-primary flex-grow sm:flex-grow-0"
      on:click={checkForUpdates}
      disabled={isChecking || isUpdating}
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

    {#if showChangelogButton}
      <button class="btn btn-secondary flex-grow sm:flex-grow-0" on:click={getChangelog} disabled={isUpdating}>
        <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
          <path fill="currentColor" d={mdiPackageVariant} />
        </svg>
        View Changelog
      </button>
    {/if}

    {#if showUpgradeButton}
      <button class="btn btn-accent flex-grow sm:flex-grow-0" on:click={startUpdate} disabled={isUpdating}>
        {#if isUpdating}
          <span class="loading loading-spinner"></span>
        {:else}
          <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
            <path fill="currentColor" d={mdiCog} />
          </svg>
        {/if}
        Upgrade
      </button>
    {/if}
  </div>

  {#if isUpdating}
    <div class="mt-4 p-4 bg-base-200 rounded-lg">
      <h3 class="text-lg font-semibold mb-2">Update in Progress</h3>
      <p>The system is being updated. This may take several minutes and the system may reboot.</p>
      <progress class="progress progress-primary w-full mt-2" max="100"></progress>
    </div>
  {/if}

  {#if showChangelog}
    <div class="modal modal-open">
      <div class="modal-box max-w-3xl w-full">
        <h3 class="font-bold text-lg mb-4">Changelog</h3>
        <div class="py-4 max-h-96 overflow-y-auto">
          {@html changelog}
        </div>
        <div class="modal-action">
          <button class="btn" on:click={() => showChangelog = false}>Close</button>
        </div>
      </div>
    </div>
  {/if}
</div>