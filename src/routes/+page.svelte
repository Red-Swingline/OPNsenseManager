<script lang="ts">
  import { onMount } from 'svelte';
  import { invoke } from "@tauri-apps/api/core";
  import Login from '$lib/components/forms/Login.svelte';
  import AppLayout from './AppLayout.svelte';
  import InitialSetupForm from '$lib/components/forms/InitialSetupForm.svelte';
  import { toasts } from '$lib/stores/toastStore';
  import { authStore } from '$lib/stores/authStore';
  import { goto } from '$app/navigation';

  let isFirstRun: boolean | null = null;
  let isLoading = true;

  onMount(async () => {
    try {
      isFirstRun = await invoke<boolean>("check_first_run");
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

  async function handleInitialSetup(event: CustomEvent<{apiKey: string, apiSecret: string, apiUrl: string, port: number, pin: string}>) {
    const { apiKey, apiSecret, apiUrl, port, pin } = event.detail;
    console.log("Saving initial config...");

    try {
      await invoke("save_initial_config", { 
        apiKey, 
        apiSecret, 
        apiUrl, 
        port,
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

  function handleFormError(event: CustomEvent<{message: string}>) {
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
  <div class="min-h-screen bg-base-200 p-4">
    <div class="max-w-md mx-auto space-y-8">
      <div class="text-center">
        <h1 class="text-3xl font-bold mb-2">Welcome to OPNsense Manager</h1>
        <p class="text-base-content">Please enter your API information and create a PIN to get started.</p>
      </div>
      <div class="card bg-base-100 shadow-xl">
        <InitialSetupForm 
          on:submit={handleInitialSetup}
          on:error={handleFormError}
        />
      </div>
    </div>
  </div>
{:else if !$authStore.isLoggedIn}
  <Login on:login={handleLogin} />
{:else}
  <AppLayout>
    <div class="text-center p-4">
      <h2 class="text-2xl font-bold mb-4">Welcome to OPNsense Manager</h2>
      <p class="text-base-content">This is the main interface of OPNsense Manager. Add your content here.</p>
    </div>
  </AppLayout>
{/if}