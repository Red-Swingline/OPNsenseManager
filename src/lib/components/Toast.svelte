<script lang="ts">
    import { fade, fly } from 'svelte/transition';
    import { toasts, type Toast } from '$lib/stores/toastStore';
    import { mdiCheckCircle, mdiAlertCircle, mdiInformation, mdiAlert } from '@mdi/js';
  
    const icons = {
      success: mdiCheckCircle,
      error: mdiAlertCircle,
      info: mdiInformation,
      warning: mdiAlert
    };
  
    function getAlertClass(type: Toast['type']) {
      switch (type) {
        case 'success': return 'alert-success';
        case 'error': return 'alert-error';
        case 'warning': return 'alert-warning';
        default: return 'alert-info';
      }
    }
  </script>
  
  <div class="toast-container">
    {#each $toasts as toast (toast.id)}
      <div
        class="alert {getAlertClass(toast.type)} shadow-lg toast-message"
        transition:fly={{ y: 200, duration: 300 }}
        on:click={() => toasts.remove(toast.id)}
      >
        <div class="flex items-center w-full">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={icons[toast.type]} />
          </svg>
          <span class="flex-grow">{toast.message}</span>
        </div>
      </div>
    {/each}
  </div>
  
  <style>
    .toast-container {
      position: fixed;
      top: 1rem;
      right: 1rem;
      left: 1rem;
      z-index: 1000;
      display: flex;
      flex-direction: column;
      align-items: flex-end;
    }
  
    .toast-message {
      width: 100%;
      max-width: 600px;
      margin-bottom: 0.5rem;
      cursor: pointer;
    }
  
    @media (min-width: 640px) {
      .toast-message {
        width: 80%;
      }
    }
  
    @media (min-width: 768px) {
      .toast-message {
        width: 60%;
      }
    }
  
    @media (min-width: 1024px) {
      .toast-message {
        width: 40%;
      }
    }
  </style>