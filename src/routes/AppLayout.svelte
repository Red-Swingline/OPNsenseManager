<script lang="ts">
  import { mdiMenu, mdiHome, mdiCog, mdiLogout, mdiRouter, mdiShieldSearch, mdiWallFire } from '@mdi/js';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/authStore';
  import { page } from '$app/stores';
  
  export let title = 'OPNsense Manager';
  let isSidebarOpen = false;

  const menuItems = [
    { path: '/', icon: mdiHome, label: 'Home' },
    { path: '/devices', icon: mdiRouter, label: 'Devices' },
    { path: '/alias', icon: mdiShieldSearch, label: 'Alias' },
    { path: '/rules', icon: mdiWallFire, label: 'Firewall Rules' },
    { path: '/settings', icon: mdiCog, label: 'Settings' },
  ];

  function toggleSidebar() {
    isSidebarOpen = !isSidebarOpen;
  }

  function handleLogout() {
    authStore.logout();
    goto('/');
    isSidebarOpen = false;
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' || event.key === ' ') {
      toggleSidebar();
    }
  }

  function handleOverlayKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' || event.key === ' ' || event.key === 'Escape') {
      toggleSidebar();
    }
  }

  function handleNavigation(path: string) {
    if ($page.url.pathname !== path) {
      goto(path);
    }
    isSidebarOpen = false;
  }
</script>

<div class="flex h-screen bg-base-200">
  <!-- Sidebar -->
  <aside class="hidden lg:flex flex-col w-64 bg-base-100">
    <div class="flex items-center justify-center h-16 bg-primary">
      <span class="text-xl font-bold text-base-100">{title}</span>
    </div>
    <nav class="flex-1 overflow-y-auto">
      <ul class="p-2 space-y-2">
        {#each menuItems as item}
          <li>
            <button 
              on:click={() => handleNavigation(item.path)} 
              class="flex items-center w-full p-2 space-x-3 rounded-md hover:bg-base-200 transition-colors duration-200"
              class:bg-base-300={$page.url.pathname === item.path}
            >
              <svg class="w-6 h-6" viewBox="0 0 24 24">
                <path fill="currentColor" d={item.icon} />
              </svg>
              <span>{item.label}</span>
            </button>
          </li>
        {/each}
        <li>
          <button on:click={handleLogout} class="flex items-center w-full p-2 space-x-3 rounded-md hover:bg-base-200 transition-colors duration-200">
            <svg class="w-6 h-6" viewBox="0 0 24 24">
              <path fill="currentColor" d={mdiLogout} />
            </svg>
            <span>Logout</span>
          </button>
        </li>
      </ul>
    </nav>
  </aside>

  <!-- Main content -->
  <div class="flex-1 flex flex-col overflow-hidden">
    <!-- Top navbar -->
    <header class="bg-base-100 border-b border-base-300">
      <div class="flex items-center justify-between p-4">
        <div class="flex items-center space-x-4">
          <button 
            type="button"
            class="lg:hidden p-1 rounded-md hover:bg-base-200 transition-colors duration-200" 
            on:click={toggleSidebar}
            on:keydown={handleKeydown}
            aria-label="Toggle sidebar"
          >
            <svg class="w-6 h-6" viewBox="0 0 24 24">
              <path fill="currentColor" d={mdiMenu} />
            </svg>
          </button>
          <h1 class="text-xl font-semibold">{title}</h1>
        </div>
        <!-- Add any additional navbar items here -->
      </div>
    </header>

    <!-- Page content -->
    <main class="flex-1 overflow-y-auto bg-base-200 p-6">
      <slot></slot>
    </main>
  </div>

  <!-- Mobile sidebar -->
  {#if isSidebarOpen}
    <div 
      class="fixed inset-0 z-50 lg:hidden" 
      on:click={toggleSidebar}
      on:keydown={handleOverlayKeydown}
      tabindex="0"
      role="button"
      aria-label="Close sidebar"
    >
      <div class="absolute inset-0 bg-base-300 opacity-75"></div>
    </div>

    <aside class="fixed inset-y-0 left-0 z-50 w-64 bg-base-100 lg:hidden">
      <div class="flex items-center justify-center h-16 bg-primary">
        <span class="text-xl font-bold text-base-100">{title}</span>
      </div>
      <nav class="mt-5">
        <ul class="p-2 space-y-2">
          {#each menuItems as item}
            <li>
              <button 
                on:click={() => handleNavigation(item.path)} 
                class="flex items-center w-full p-2 space-x-3 rounded-md hover:bg-base-200 transition-colors duration-200"
                class:bg-base-300={$page.url.pathname === item.path}
              >
                <svg class="w-6 h-6" viewBox="0 0 24 24">
                  <path fill="currentColor" d={item.icon} />
                </svg>
                <span>{item.label}</span>
              </button>
            </li>
          {/each}
          <li>
            <button on:click={handleLogout} class="flex items-center w-full p-2 space-x-3 rounded-md hover:bg-base-200 transition-colors duration-200">
              <svg class="w-6 h-6" viewBox="0 0 24 24">
                <path fill="currentColor" d={mdiLogout} />
              </svg>
              <span>Logout</span>
            </button>
          </li>
        </ul>
      </nav>
    </aside>
  {/if}
</div>