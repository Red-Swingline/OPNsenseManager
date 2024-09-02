<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { invoke } from "@tauri-apps/api/core";
  import AppLayout from '../AppLayout.svelte';
  import { authStore } from '$lib/stores/authStore';
  import { mdiRefresh } from '@mdi/js';

  interface FirewallRule {
    uuid: string;
    enabled: string;
    sequence: string;
    description: string;
    isToggling?: boolean;
  }

  let rules: FirewallRule[] = [];
  let isLoading = true;
  let error: string | null = null;
  let refreshInterval: number;
  const REFRESH_INTERVAL = 30000; // 30 seconds

  onMount(async () => {
    if ($authStore.isLoggedIn) {
      await fetchRules();
      startPeriodicRefresh();
    }
  });

  onDestroy(() => {
    stopPeriodicRefresh();
  });

  function startPeriodicRefresh() {
    refreshInterval = setInterval(updateRules, REFRESH_INTERVAL);
  }

  function stopPeriodicRefresh() {
    if (refreshInterval) {
      clearInterval(refreshInterval);
    }
  }

  async function fetchRules() {
    isLoading = true;
    error = null;
    try {
      const response = await invoke<{rows: FirewallRule[]}>("get_firewall_rules");
      rules = response.rows;
    } catch (err) {
      console.error("Failed to fetch firewall rules:", err);
      error = err instanceof Error ? err.message : "An unexpected error occurred";
    } finally {
      isLoading = false;
    }
  }

  async function toggleRule(rule: FirewallRule) {
    const originalStatus = rule.enabled;
    try {
      rule.isToggling = true;
      const toggleResponse = await invoke<{result: string, changed: boolean}>("toggle_firewall_rule", { uuid: rule.uuid });
      if (toggleResponse.changed) {
        const applyResponse = await invoke<{status: string}>("apply_firewall_changes");
        if (applyResponse.status.trim() === "OK") {
          await updateRules();
        } else {
          throw new Error("Failed to apply changes");
        }
      }
    } catch (err) {
      console.error("Failed to toggle firewall rule:", err);
      rule.enabled = originalStatus; 
    } finally {
      rule.isToggling = false;
    }
  }

  async function updateRules() {
    try {
      const response = await invoke<{rows: FirewallRule[]}>("get_firewall_rules");
      const newRules = response.rows;
      
      let hasChanges = false;
      newRules.forEach((newRule, index) => {
        if (JSON.stringify(newRule) !== JSON.stringify(rules[index])) {
          hasChanges = true;
          rules[index] = newRule;
        }
      });

      if (hasChanges) {
        rules = [...rules]; 
      }
    } catch (err) {
      console.error("Failed to update firewall rules:", err);
    }
  }

  function manualRefresh() {
    stopPeriodicRefresh();
    fetchRules().then(() => startPeriodicRefresh());
  }
</script>

<AppLayout>
  <div class="max-w-6xl mx-auto">
    <h2 class="text-2xl font-bold mb-6">Firewall Rules</h2>
    
    {#if isLoading}
      <div class="text-center">
        <span class="loading loading-spinner loading-lg"></span>
        <p class="mt-4 text-base-content">Loading firewall rules...</p>
      </div>
    {:else if error}
      <p class="text-error">Error: {error}</p>
    {:else if rules.length === 0}
      <p class="text-base-content">No firewall rules found.</p>
    {:else}
      <div class="space-y-4">
        {#each rules as rule (rule.uuid)}
          <div class="card bg-base-100 shadow-xl">
            <div class="card-body p-4 flex flex-row items-center justify-between">
              <h3 class="card-title text-lg">{rule.description || 'Unnamed Rule'}</h3>
              <label class="swap swap-flip">
                <input 
                  type="checkbox" 
                  checked={rule.enabled === "1"}
                  on:change={() => toggleRule(rule)}
                  disabled={rule.isToggling}
                />
                <div class="swap-on bg-success text-success-content rounded-full w-14 h-8 flex items-center justify-center">ON</div>
                <div class="swap-off bg-error text-error-content rounded-full w-14 h-8 flex items-center justify-center">OFF</div>
              </label>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>

  <!-- Floating Action Button -->
  <div class="fixed bottom-6 right-6">
    <button
      on:click={manualRefresh}
      class="btn btn-circle btn-lg btn-primary shadow-lg"
      title="Refresh Rules"
    >
      <svg class="w-6 h-6" viewBox="0 0 24 24">
        <path fill="currentColor" d={mdiRefresh} />
      </svg>
    </button>
  </div>
</AppLayout>

<style>
  .btn-circle {
    @apply rounded-full w-14 h-14 p-0 grid place-items-center;
  }
  
  .btn-lg {
    @apply w-16 h-16;
  }

  .swap-on, .swap-off {
    @apply font-bold text-sm;
  }
</style>