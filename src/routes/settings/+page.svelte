<script lang="ts">
  import { onMount } from 'svelte';
  import { invoke } from "@tauri-apps/api/core";
  import AppLayout from '../AppLayout.svelte';
  import SettingsForm from '../SettingsForm.svelte';
  import Login from '../Login.svelte';
  import { toasts } from '$lib/stores/toastStore';
  import { authStore } from '$lib/stores/authStore';

  let apiKey = "";
  let apiSecret = "";
  let apiUrl = "";
  let port = 443;
  let currentPin = "";
  let newPin = "";
  let confirmNewPin = "";
  let activeTab: 'api' | 'pin' = 'api';

  onMount(async () => {
    try {
      const apiInfo = await invoke<{
        api_key: string;
        api_secret: string;
        api_url: string;
        port: number;
      }>("get_api_info");
      if (apiInfo) {
        apiKey = apiInfo.api_key;
        apiSecret = apiInfo.api_secret;
        apiUrl = apiInfo.api_url;
        port = apiInfo.port;
      }
    } catch (error) {
      console.error("Failed to fetch API info:", error);
      toasts.error("Failed to load settings. Please try again.");
    }
  });

  async function handleApiSubmit() {
    try {
      await invoke("update_api_info", { apiKey, apiSecret, apiUrl, port: Number(port) });
      toasts.success("API information updated successfully!");
    } catch (error) {
      console.error("Failed to update API info:", error);
      toasts.error("Failed to update API information. Please try again.");
    }
  }

  async function handlePinSubmit() {
    if (newPin !== confirmNewPin) {
      toasts.error("New PINs do not match.");
      return;
    }

    if (!/^\d+$/.test(newPin)) {
      toasts.error("PIN must contain only numbers.");
      return;
    }

    try {
      await invoke("update_pin", { currentPin, newPin, confirmNewPin });
      toasts.success("PIN updated successfully!");
      currentPin = "";
      newPin = "";
      confirmNewPin = "";
    } catch (error) {
      console.error("Failed to update PIN:", error);
      if (error instanceof Error) {
        toasts.error(error.message);
      } else {
        toasts.error("An unknown error occurred.");
      }
    }
  }

  function setActiveTab(tab: 'api' | 'pin') {
    activeTab = tab;
  }

  function handleKeydown(event: KeyboardEvent, tab: 'api' | 'pin') {
    if (event.key === 'Enter' || event.key === ' ') {
      setActiveTab(tab);
    }
  }
</script>

{#if $authStore.isLoggedIn}
  <AppLayout>
    <div class="max-w-4xl mx-auto">
      <h2 class="text-2xl font-bold mb-6">Settings</h2>
      
      <div class="tabs tabs-boxed mb-6">
        <button 
          type="button"
          class="tab {activeTab === 'api' ? 'tab-active' : ''}" 
          on:click={() => setActiveTab('api')}
          on:keydown={(e) => handleKeydown(e, 'api')}
        >
          API Settings
        </button>
        <button 
          type="button"
          class="tab {activeTab === 'pin' ? 'tab-active' : ''}" 
          on:click={() => setActiveTab('pin')}
          on:keydown={(e) => handleKeydown(e, 'pin')}
        >
          Change PIN
        </button>
      </div>

      {#if activeTab === 'api'}
        <div class="bg-base-100 p-6 rounded-lg shadow-lg">
          <h3 class="text-xl font-semibold mb-4">API Configuration</h3>
          <SettingsForm 
            {apiKey}
            {apiSecret}
            {apiUrl}
            {port}
            on:submit={handleApiSubmit}
          />
        </div>
      {:else if activeTab === 'pin'}
        <div class="bg-base-100 p-6 rounded-lg shadow-lg">
          <h3 class="text-xl font-semibold mb-4">Change PIN</h3>
          <form on:submit|preventDefault={handlePinSubmit} class="space-y-4">
            <div class="form-control">
              <label class="label" for="currentPin">
                <span class="label-text">Current PIN</span>
              </label>
              <input 
                id="currentPin"
                bind:value={currentPin}
                type="password"
                inputmode="numeric"
                pattern="\d*"
                placeholder="Enter current PIN"
                class="input input-bordered w-full"
                required
              />
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="form-control">
                <label class="label" for="newPin">
                  <span class="label-text">New PIN</span>
                </label>
                <input 
                  id="newPin"
                  bind:value={newPin}
                  type="password"
                  inputmode="numeric"
                  pattern="\d*"
                  placeholder="Enter new PIN"
                  class="input input-bordered w-full"
                  required
                />
              </div>
              <div class="form-control">
                <label class="label" for="confirmNewPin">
                  <span class="label-text">Confirm New PIN</span>
                </label>
                <input 
                  id="confirmNewPin"
                  bind:value={confirmNewPin}
                  type="password"
                  inputmode="numeric"
                  pattern="\d*"
                  placeholder="Confirm new PIN"
                  class="input input-bordered w-full"
                  required
                />
              </div>
            </div>
            <div class="flex justify-end mt-6">
              <button type="submit" class="btn btn-primary">Update PIN</button>
            </div>
          </form>
        </div>
      {/if}
    </div>
  </AppLayout>
{:else}
  <Login />
{/if}