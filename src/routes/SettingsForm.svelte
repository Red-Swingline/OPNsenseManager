<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let apiKey = "";
  export let apiSecret = "";
  export let apiUrl = "";
  export let port = 443;
  export let pin = "";

  const dispatch = createEventDispatcher();

  function handleSubmit(event: Event) {
      event.preventDefault();
      console.log("SettingsForm - handleSubmit called");
      console.log("SettingsForm - Current form values:", { apiKey, apiSecret, apiUrl, port, pin });
      
      if (validatePin(pin)) {
          console.log("SettingsForm - PIN is valid, dispatching submit event");
          dispatch('submit', { apiKey, apiSecret, apiUrl, port, pin });
      } else {
          console.log("SettingsForm - PIN is invalid, dispatching error event");
          dispatch('error', { message: "PIN must contain only numbers." });
      }
  }

  function validatePin(input: string): boolean {
      console.log("SettingsForm - validatePin called with input:", input);
      const isValid = /^\d+$/.test(input);
      console.log("SettingsForm - PIN is valid:", isValid);
      return isValid;
  }
</script>

<form on:submit={handleSubmit} class="space-y-6">
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="form-control">
          <label class="label" for="apiKey">
              <span class="label-text">API Key</span>
          </label>
          <input 
              id="apiKey" 
              bind:value={apiKey} 
              type="text" 
              placeholder="API Key" 
              class="input input-bordered w-full" 
              required 
          />
      </div>

      <div class="form-control">
          <label class="label" for="apiSecret">
              <span class="label-text">API Secret</span>
          </label>
          <input 
              id="apiSecret" 
              bind:value={apiSecret} 
              type="password" 
              placeholder="API Secret" 
              class="input input-bordered w-full" 
              required 
          />
      </div>

      <div class="form-control">
          <label class="label" for="apiUrl">
              <span class="label-text">API URL</span>
          </label>
          <input 
              id="apiUrl" 
              bind:value={apiUrl} 
              type="url" 
              placeholder="API URL" 
              class="input input-bordered w-full" 
              required 
          />
      </div>

      <div class="form-control">
          <label class="label" for="port">
              <span class="label-text">Port</span>
          </label>
          <input 
              id="port" 
              bind:value={port} 
              type="number" 
              placeholder="Port" 
              class="input input-bordered w-full" 
              required 
          />
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
  </div>

  <div class="flex justify-end">
      <button type="submit" class="btn btn-primary">Save Configuration</button>
  </div>
</form>