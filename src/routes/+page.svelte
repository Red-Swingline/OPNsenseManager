<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { invoke } from "@tauri-apps/api/core";
  import Login from "$lib/components/forms/Login.svelte";
  import AppLayout from "./AppLayout.svelte";
  import InitialSetupForm from "$lib/components/forms/InitialSetupForm.svelte";
  import { toasts } from "$lib/stores/toastStore";
  import { authStore } from "$lib/stores/authStore";
  import { goto } from "$app/navigation";
  import {
    mdiArrowUp,
    mdiArrowDown,
    mdiRestart,
    mdiChevronDown,
    mdiChevronUp,
  } from "@mdi/js";

  interface InterfaceData {
    name: string;
    "bytes received": string;
    "bytes transmitted": string;
    device: string;
    driver: string;
  }

  interface InterfaceTraffic {
    interfaces: Record<string, InterfaceData>;
    time: number;
  }

  interface DashboardData {
    gatewayStatus: any;
    services: any;
    interfaceTraffic: InterfaceTraffic | null;
  }

  let isFirstRun: boolean | null = null;
  let isLoading = true;
  let dashboardData: DashboardData = {
    gatewayStatus: null,
    services: null,
    interfaceTraffic: null
  };
  let expandedGateway: string | null = null;
  let pollInterval: number;
  let progressInterval: number;
  let progress = 0;
  const UPDATE_INTERVAL = 5000; // 5 seconds

  $: sortedInterfaces = dashboardData.interfaceTraffic 
    ? Object.entries(dashboardData.interfaceTraffic.interfaces)
        .sort(([, a], [, b]) => a.name.localeCompare(b.name))
    : [];

  onMount(async () => {
    try {
      isFirstRun = await invoke<boolean>("check_first_run");
      console.log("Is first run:", isFirstRun);

      if (!isFirstRun) {
        authStore.setConfigured(true);
        if ($authStore.isLoggedIn) {
          await loadDashboardData();
          startPolling();
        }
      }
    } catch (error) {
      console.error("Failed to check if first run:", error);
      toasts.error("Failed to initialize application. Please try again.");
    } finally {
      isLoading = false;
    }
  });

  onDestroy(() => {
    if (pollInterval) clearInterval(pollInterval);
    if (progressInterval) clearInterval(progressInterval);
  });

  async function loadDashboardData() {
    try {
      const [gatewayStatus, services, interfaceTraffic] = await Promise.all([
        invoke<any>("get_gateway_status"),
        invoke<any>("get_services"),
        invoke<InterfaceTraffic>("get_interface_traffic")
      ]);

      dashboardData = { gatewayStatus, services, interfaceTraffic };
      console.log("Dashboard Data:", dashboardData);
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
      toasts.error("Failed to load dashboard data. Please try again.");
    }
  }

  function startPolling() {
    pollInterval = setInterval(async () => {
      try {
        const interfaceTraffic = await invoke<InterfaceTraffic>("get_interface_traffic");
        dashboardData.interfaceTraffic = interfaceTraffic;
        progress = 0;
      } catch (error) {
        console.error("Failed to fetch traffic data:", error);
      }
    }, UPDATE_INTERVAL);

    progressInterval = setInterval(() => {
      progress += (100 / (UPDATE_INTERVAL / 100));
      if (progress >= 100) progress = 0;
    }, 100);
  }

  async function restartService(serviceId: string) {
    try {
      await invoke("restart_service", { serviceId });
      toasts.success(`Service ${serviceId} restarted successfully`);
      await loadDashboardData();
    } catch (error) {
      console.error(`Failed to restart service ${serviceId}:`, error);
      toasts.error(`Failed to restart service ${serviceId}. Please try again.`);
    }
  }

  async function handleInitialSetup(event: CustomEvent<{
    profileName: string;
    apiKey: string;
    apiSecret: string;
    apiUrl: string;
    port: number;
    pin: string;
  }>) {
    const { profileName, apiKey, apiSecret, apiUrl, port, pin } = event.detail;
    console.log("Saving initial config...");

    try {
      await invoke("save_initial_config", {
        config: {
          profile_name: profileName,
          api_key: apiKey,
          api_secret: apiSecret,
          api_url: apiUrl,
          port,
          pin,
        },
      });

      console.log("Configuration saved successfully");
      isFirstRun = false;
      authStore.setConfigured(true);
      toasts.success("Configuration saved successfully!");

      setTimeout(() => goto("/"), 100);
    } catch (error) {
      console.error("Failed to save configuration:", error);
      toasts.error(`Failed to save configuration: ${error}`);
    }
  }

  function handleFormError(event: CustomEvent<{ message: string }>) {
    toasts.error(event.detail.message);
  }

  async function handleLogin() {
    authStore.login();
    await loadDashboardData();
    startPolling();
  }

  function toggleGatewayExpansion(gatewayName: string) {
    expandedGateway = expandedGateway === gatewayName ? null : gatewayName;
  }

  function formatBytes(bytes: string): string {
    const parsedBytes = parseInt(bytes);
    if (isNaN(parsedBytes)) return "0 B";
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    if (parsedBytes === 0) return '0 B';
    const i = Math.floor(Math.log(parsedBytes) / Math.log(1024));
    return Math.round(parsedBytes / Math.pow(1024, i)) + ' ' + sizes[i];
  }
</script>

<style>
  @keyframes rotate {
    100% {
      transform: rotate(360deg);
    }
  }

  .progress-ring {
    animation: rotate 5s linear infinite;
  }
</style>

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
        <p class="text-base-content">
          Please enter your API information and create a PIN to get started.
        </p>
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
    <div class="p-4 max-w-3xl mx-auto">
      <h2 class="text-2xl font-bold mb-4">OPNsense Dashboard</h2>

      {#if dashboardData.gatewayStatus && dashboardData.services && dashboardData.interfaceTraffic}
        <div class="space-y-4">
          <!-- Interface Traffic -->
          <div class="card bg-base-100 shadow-xl relative">
            <div class="card-body">
              <div class="flex justify-between items-center">
                <h3 class="card-title text-lg">Interface Traffic</h3>
                <svg class="progress-ring" width="24" height="24" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" fill="none" stroke="#e5e7eb" stroke-width="2" />
                  <circle
                    cx="12"
                    cy="12"
                    r="10"
                    fill="none"
                    stroke="#4f46e5"
                    stroke-width="2"
                    stroke-dasharray="62.83185307179586"
                    stroke-dashoffset={62.83185307179586 * (1 - progress / 100)}
                    transform="rotate(-90 12 12)"
                  />
                </svg>
              </div>
              <div class="overflow-x-auto">
                <table class="table w-full">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Device</th>
                      <th>Driver</th>
                      <th>Bytes Received</th>
                      <th>Bytes Transmitted</th>
                    </tr>
                  </thead>
                  <tbody>
                    {#each sortedInterfaces as [key, interfaceData]}
                      <tr>
                        <td>{interfaceData.name}</td>
                        <td>{interfaceData.device}</td>
                        <td>{interfaceData.driver}</td>
                        <td>{formatBytes(interfaceData["bytes received"])}</td>
                        <td>{formatBytes(interfaceData["bytes transmitted"])}</td>
                      </tr>
                    {/each}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Gateway Status -->
          <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
              <h3 class="card-title text-lg mb-2">Gateways</h3>
              <ul class="space-y-2">
                {#each dashboardData.gatewayStatus.items as gateway}
                  <li class="border rounded-lg p-3">
                    <div
                      class="flex justify-between items-center cursor-pointer"
                      on:click={() => toggleGatewayExpansion(gateway.name)}
                    >
                      <div>
                        <div class="font-medium">{gateway.name}</div>
                        <div class="text-sm opacity-50">{gateway.address}</div>
                      </div>
                      <span
                        class="badge {gateway.status_translated === 'Online'
                          ? 'badge-success'
                          : 'badge-error'}"
                      >
                        {gateway.status_translated}
                      </span>
                      <svg class="w-5 h-5" viewBox="0 0 24 24">
                        <path
                          fill="currentColor"
                          d={expandedGateway === gateway.name
                            ? mdiChevronUp
                            : mdiChevronDown}
                        />
                      </svg>
                    </div>
                    {#if expandedGateway === gateway.name}
                      <div class="mt-2 text-sm">
                        <p>RTT: {gateway.delay === "~" ? "-" : gateway.delay}</p>
                        <p>RTTd: {gateway.stddev === "~" ? "-" : gateway.stddev}</p>
                        <p>Loss: {gateway.loss === "~" ? "-" : gateway.loss}</p>
                      </div>
                    {/if}
                  </li>
                {/each}
              </ul>
            </div>
          </div>

          <!-- Services -->
          <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
              <h3 class="card-title text-lg mb-2">Services</h3>
              <ul class="space-y-2">
                {#each dashboardData.services.rows as service}
                  <li class="border rounded-lg p-3">
                    <div class="flex justify-between items-center">
                      <div class="flex-grow">
                        <div class="font-medium">{service.name}</div>
                        <div class="text-sm opacity-50">{service.description}</div>
                      </div>
                      <div class="flex items-center space-x-3">
                        <svg
                          class="w-5 h-5 {service.running ? 'text-success' : 'text-error'}"
                          viewBox="0 0 24 24"
                          title={service.running ? "Service is running" : "Service is stopped"}
                        >
                          <path
                            fill="currentColor"
                            d={service.running ? mdiArrowUp : mdiArrowDown}
                          />
                        </svg>
                        <button
                          class="btn btn-sm btn-ghost"
                          on:click|stopPropagation={() => restartService(service.id)}
                          title="Restart Service"
                        >
                          <svg class="w-4 h-4" viewBox="0 0 24 24">
                            <path fill="currentColor" d={mdiRestart} />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </li>
                {/each}
              </ul>
            </div>
          </div>
        </div>
      {:else}
        <div class="flex justify-center items-center h-64">
          <span class="loading loading-spinner loading-lg"></span>
        </div>
      {/if}
    </div>
  </AppLayout>
{/if}