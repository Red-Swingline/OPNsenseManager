<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { invoke } from "@tauri-apps/api/core";

  export let showPin = false;

  let profiles = [];
  let selectedProfileName = "";
  let apiKey = "";
  let apiSecret = "";
  let apiUrl = "";
  let port = 443;
  let pin = "";

  const dispatch = createEventDispatcher();

  onMount(async () => {
      await loadProfiles();
  });

  async function loadProfiles() {
      try {
          profiles = await invoke('get_api_profiles');
          if (profiles.length > 0) {
              selectedProfileName = profiles.find(p => p.is_default)?.profile_name || profiles[0].profile_name;
              await loadProfileInfo(selectedProfileName);
          }
      } catch (error) {
          console.error('Failed to load profiles:', error);
          dispatch('error', { message: 'Failed to load profiles' });
      }
  }

  async function loadProfileInfo(profileName: string) {
      try {
          const profileInfo = await invoke('get_api_info', { profileName });
          if (profileInfo) {
              apiKey = profileInfo.api_key;
              apiSecret = profileInfo.api_secret;
              apiUrl = profileInfo.api_url;
              port = profileInfo.port;
          }
      } catch (error) {
          console.error('Failed to load profile info:', error);
          dispatch('error', { message: 'Failed to load profile information' });
      }
  }

  async function handleProfileChange() {
      await loadProfileInfo(selectedProfileName);
      await setDefaultProfile(selectedProfileName);
  }

  async function setDefaultProfile(profileName: string) {
      try {
          await invoke('set_default_profile', { profileName });
          profiles = profiles.map(p => ({ ...p, is_default: p.profile_name === profileName }));
          dispatch('profileChanged', { profileName });
      } catch (error) {
          console.error('Failed to set default profile:', error);
          dispatch('error', { message: 'Failed to set default profile' });
      }
  }

  async function handleSubmit() {
      try {
          await invoke('update_api_info', {
              profileName: selectedProfileName,
              apiKey,
              apiSecret,
              apiUrl,
              port: Number(port),
              isDefault: true // Always set to true as it's now the selected profile
          });
          dispatch('submit', { profileName: selectedProfileName, apiKey, apiSecret, apiUrl, port, pin });
      } catch (error) {
          console.error('Failed to update API info:', error);
          dispatch('error', { message: 'Failed to update API information' });
      }
  }
</script>

<form on:submit|preventDefault={handleSubmit} class="space-y-6">
  <div class="form-control">
      <label class="label" for="profileSelect">
          <span class="label-text">Select Profile (Default)</span>
      </label>
      <select
          id="profileSelect"
          bind:value={selectedProfileName}
          on:change={handleProfileChange}
          class="select select-bordered w-full"
      >
          {#each profiles as profile}
              <option value={profile.profile_name}>
                  {profile.profile_name} {profile.is_default ? '(Default)' : ''}
              </option>
          {/each}
      </select>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="form-control">
          <label class="label" for="apiKey">
              <span class="label-text">API Key</span>
          </label>
          <input id="apiKey" bind:value={apiKey} type="text" placeholder="API Key" class="input input-bordered w-full" required />
      </div>

      <div class="form-control">
          <label class="label" for="apiSecret">
              <span class="label-text">API Secret</span>
          </label>
          <input id="apiSecret" bind:value={apiSecret} type="password" placeholder="API Secret" class="input input-bordered w-full" required />
      </div>

      <div class="form-control">
          <label class="label" for="apiUrl">
              <span class="label-text">API URL</span>
          </label>
          <input id="apiUrl" bind:value={apiUrl} type="url" placeholder="API URL" class="input input-bordered w-full" required />
      </div>

      <div class="form-control">
          <label class="label" for="port">
              <span class="label-text">Port</span>
          </label>
          <input id="port" bind:value={port} type="number" placeholder="Port" class="input input-bordered w-full" required />
      </div>

      {#if showPin}
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
      {/if}
  </div>

  <div class="flex justify-end">
      <button type="submit" class="btn btn-primary">
          {showPin ? 'Save Configuration' : 'Update API Settings'}
      </button>
  </div>
</form>