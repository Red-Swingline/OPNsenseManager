<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { invoke } from "@tauri-apps/api/core";
  import { toasts } from '$lib/stores/toastStore';

  const dispatch = createEventDispatcher();

  let pin = "";

  async function handleSubmit() {
    if (!/^\d+$/.test(pin)) {
      toasts.error("PIN must contain only numbers.");
      return;
    }

    try {
      const result = await invoke("verify_pin", { pin });
      if (result) {
        toasts.success("Login successful!");
        dispatch('login');
      } else {
        toasts.error("Invalid PIN. Please try again.");
      }
    } catch (error) {
      console.error("Failed to verify PIN:", error);
      toasts.error("An error occurred. Please try again.");
    }
  }
</script>

<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary to-secondary p-4">
  <div class="w-full max-w-md bg-base-100 rounded-lg overflow-hidden">
    <div class="p-8">
      <div class="flex justify-center mb-8">
        <img src="/logo.png" alt="OPNsense Manager Logo" class="w-32 h-32 object-contain" />
      </div>
      <h2 class="text-2xl font-bold text-center mb-6">Welcome Back!</h2>
      <form on:submit|preventDefault={handleSubmit} class="space-y-6">
        <div>
          <label for="pin" class="block text-sm font-medium text-base-content mb-2">
            Enter your PIN
          </label>
          <input 
            id="pin"
            bind:value={pin}
            type="password"
            inputmode="numeric"
            pattern="\d*"
            placeholder="••••"
            class="input input-bordered w-full py-3 px-4 bg-base-200 text-base-content rounded-md focus:ring-2 focus:ring-primary"
            required
          />
        </div>
        <div>
          <button type="submit" class="btn btn-primary w-full py-3 px-4 rounded-md transition-all duration-300 hover:brightness-110">
            Login
          </button>
        </div>
      </form>
    </div>
  </div>
</div>