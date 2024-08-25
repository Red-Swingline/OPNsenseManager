<script lang="ts">
  import { onMount } from 'svelte';
  import { invoke } from "@tauri-apps/api/core";
  import Login from './Login.svelte';
  import AppLayout from './AppLayout.svelte';
  import SettingsForm from './SettingsForm.svelte';
  import { toasts } from '$lib/stores/toastStore';
  import { authStore } from '$lib/stores/authStore';
  import { goto } from '$app/navigation';

  let isFirstRun: boolean | null = null;
  let isLoading = true;

  onMount(async () => {
    try {
      console.log("Checking if first run...");
      isFirstRun = await invoke("check_first_run");
      console.log("Is first run:", isFirstRun);
      
      if (!isFirstRun) {
        authStore.setConfigured(true);
      }
    } catch (error) {
      console.error("Failed to check if first run:", error);
      toasts.error("Failed to initialize application. Please try again.");
    } finally {
      isLoading = false;
    }
  });

  async function handleSubmit(event: CustomEvent) {
    console.log("Main - handleSubmit called");
    console.log("Main - event object:", event);
    console.log("Main - event.detail:", event.detail);

    const { apiKey, apiSecret, apiUrl, port, pin } = event.detail;
    console.log("Main - Extracted form data:", { apiKey, apiSecret, apiUrl, port, pin });

    if (!/^\d+$/.test(pin)) {
      toasts.error("PIN must contain only numbers.");
      return;
    }
    
    try {
      console.log("Saving initial config...");
      await invoke("save_initial_config", { 
        apiKey, 
        apiSecret, 
        apiUrl, 
        port: Number(port),
        pin 
      });
      
      console.log("Configuration saved successfully");
      isFirstRun = false;
      authStore.setConfigured(true);
      toasts.success("Configuration saved successfully!");
      goto('/');
    } catch (error) {
      console.error("Failed to save configuration:", error);
      toasts.error(`Failed to save configuration: ${error}`);
    }
  }

  function handleFormError(event: CustomEvent) {
    console.log("Main - handleFormError called with message:", event.detail.message);
    toasts.error(event.detail.message);
  }

  function handleLogin() {
    authStore.login();
  }
</script>

{#if isLoading}
  <div class="min-h-screen flex items-center justify-center bg-base-200">
    <div class="text-center">
      <span class="loading loading-spinner loading-lg"></span>
      <p class="mt-4 text-base-content">Loading...</p>
    </div>
  </div>
{:else if isFirstRun}
  <div class="hero min-h-screen bg-base-200">
    <div class="hero-content flex-col lg:flex-row-reverse">
      <div class="text-center lg:text-left">
        <h1 class="text-5xl font-bold">Welcome to OPNsense Manager</h1>
        <p class="py-6">Please enter your API information and create a PIN to get started.</p>
      </div>
      <div class="card flex-shrink-0 w-full max-w-sm shadow-2xl bg-base-100">
        <SettingsForm 
          on:submit={handleSubmit}
          on:error={handleFormError}
        />
      </div>
    </div>
  </div>
{:else if !$authStore.isLoggedIn}
  <Login on:login={handleLogin} />
{:else}
  <AppLayout>
    <div class="text-center">
      <h2 class="text-2xl font-bold mb-4">Welcome to OPNsense Manager</h2>
      <p class="text-base-content">This is the main interface of OPNsense Manager. Add your content here.</p>
    </div>
  </AppLayout>
{/if}