<script lang="ts">
    import { createEventDispatcher } from 'svelte';
  
    export let apiKey = "";
    export let apiSecret = "";
    export let apiUrl = "";
    export let port = 443;
    export let pin = "";
  
    const dispatch = createEventDispatcher();
  
    function handleSubmit() {
      if (!/^\d+$/.test(pin)) {
        dispatch('error', { message: "PIN must contain only numbers." });
        return;
      }
      dispatch('submit', { apiKey, apiSecret, apiUrl, port: Number(port), pin });
    }
  </script>
  
  <form on:submit|preventDefault={handleSubmit} class="space-y-4 p-4">
    <div class="form-control">
      <label class="label" for="apiKey">
        <span class="label-text">API Key</span>
      </label>
      <input id="apiKey" bind:value={apiKey} type="text" placeholder="Enter API Key" class="input input-bordered w-full" required />
    </div>
  
    <div class="form-control">
      <label class="label" for="apiSecret">
        <span class="label-text">API Secret</span>
      </label>
      <input id="apiSecret" bind:value={apiSecret} type="password" placeholder="Enter API Secret" class="input input-bordered w-full" required />
    </div>
  
    <div class="form-control">
      <label class="label" for="apiUrl">
        <span class="label-text">API URL</span>
      </label>
      <input id="apiUrl" bind:value={apiUrl} type="url" placeholder="Enter API URL" class="input input-bordered w-full" required />
    </div>
  
    <div class="form-control">
      <label class="label" for="port">
        <span class="label-text">Port</span>
      </label>
      <input id="port" bind:value={port} type="number" placeholder="Enter Port" class="input input-bordered w-full" required />
    </div>
  
    <div class="form-control">
      <label class="label" for="pin">
        <span class="label-text">PIN</span>
      </label>
      <input 
        id="pin"
        bind:value={pin}
        type="password"
        inputmode="numeric"
        pattern="\d*"
        placeholder="Enter PIN"
        class="input input-bordered w-full"
        required
      />
    </div>
  
    <div class="form-control mt-6">
      <button type="submit" class="btn btn-primary w-full">
        Save Configuration
      </button>
    </div>
  </form>