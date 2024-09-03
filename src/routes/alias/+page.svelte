<script lang="ts">
  import { onMount } from "svelte";
  import { invoke } from "@tauri-apps/api/core";
  import { debounce } from "lodash-es";
  import AppLayout from "../AppLayout.svelte";
  import { toasts } from "$lib/stores/toastStore";
  import { authStore } from "$lib/stores/authStore";
  import { mdiRefresh, mdiMagnify, mdiPlus, mdiClose } from "@mdi/js";

  interface Alias {
    name: string;
    description: string;
  }

  interface AliasDetails {
    uuid: string;
    enabled: string;
    name: string;
    description: string;
    type: string;
    content: string;
    current_items: string;
    last_updated: string;
    categories_uuid: string[];
  }

  interface AliasItemsResponse {
    rows: AliasDetails[];
  }

  let aliases: Record<string, Alias> = {};
  let aliasDetails: Record<string, AliasDetails> = {};
  let filteredAliases: Record<string, Alias> = {};
  let isLoading = true;
  let isAddingIp = false;
  let error: string | null = null;
  let selectedAlias: AliasDetails | null = null;
  let isModalOpen = false;
  let newIpAddress = "";
  let filter = "";
  let ipToRemove: string | null = null;
  let selectedIndex = -1;

  const debouncedApplyFilter = debounce(applyFilter, 300);

  onMount(() => {
    if ($authStore.isLoggedIn) {
      fetchAliasesAndDetails();
    }
    window.addEventListener("keydown", handleKeydown);
    return () => {
      window.removeEventListener("keydown", handleKeydown);
    };
  });

  async function fetchAliasesAndDetails(): Promise<void> {
    isLoading = true;
    error = null;
    try {
      const detailsResult = await invoke<AliasItemsResponse>("search_alias_items");

      console.log(
        "Full JSON result from search_alias_items:",
        JSON.stringify(detailsResult, null, 2),
      );

      if (detailsResult && detailsResult.rows) {
        aliases = detailsResult.rows.reduce((acc, item) => {
          if (!item.name.startsWith("bogons") && !item.name.startsWith("__") && !item.name.startsWith("virusprot") && !item.name.startsWith("sshlockout")) {
            acc[item.name] = {
              name: item.name,
              description: item.description,
            };
          }
          return acc;
        }, {} as Record<string, Alias>);

        aliasDetails = detailsResult.rows.reduce((acc, item) => {
          if (!item.name.startsWith("__")) {
            acc[item.name] = item;
          }
          return acc;
        }, {} as Record<string, AliasDetails>);

        console.log("Processed aliasDetails:", JSON.stringify(aliasDetails, null, 2));
      } else {
        throw new Error("Invalid response from search_alias_items");
      }

      applyFilter();
    } catch (err) {
      console.error("Failed to fetch aliases:", err);
      error = err instanceof Error ? err.message : "An unexpected error occurred";
      toasts.error(`Failed to fetch aliases: ${error}`);
    } finally {
      isLoading = false;
    }
  }

  function applyFilter(): void {
    filteredAliases = Object.fromEntries(
      Object.entries(aliases).filter(
        ([_, alias]) =>
          alias.name.toLowerCase().includes(filter.toLowerCase()) ||
          alias.description.toLowerCase().includes(filter.toLowerCase()),
      ),
    );
    selectedIndex = -1;
  }

  function openAliasDetails(alias: Alias): void {
    console.log("Opening details for alias:", alias);
    console.log(
      "Full aliasDetails object:",
      JSON.stringify(aliasDetails, null, 2),
    );
    selectedAlias = aliasDetails[alias.name];
    console.log(
      "Selected alias details:",
      JSON.stringify(selectedAlias, null, 2),
    );
    isModalOpen = true;
  }

  async function addIpToAlias(): Promise<void> {
    if (!newIpAddress || !selectedAlias) return;

    isAddingIp = true;
    try {
      const currentContent = selectedAlias.content || "";
      const updatedContent = currentContent ? `${currentContent}\n${newIpAddress}` : newIpAddress;

      await invoke("add_ip_to_alias", {
        uuid: selectedAlias.uuid,
        currentContent: updatedContent,
        newIp: newIpAddress,
      });

      await refreshAliasDetails(selectedAlias.name);
      newIpAddress = "";
      toasts.success("IP address added successfully");
    } catch (err) {
      console.error("Failed to add IP address:", err);
      toasts.error(
        `Failed to add IP address: ${err instanceof Error ? err.message : String(err)}`,
      );
    } finally {
      isAddingIp = false;
    }
  }

  function showRemoveConfirmation(ip: string): void {
    ipToRemove = ip;
  }

  async function confirmRemoveIp(): Promise<void> {
    if (ipToRemove) {
      await removeIpFromAlias(ipToRemove);
      ipToRemove = null;
    }
  }

  function cancelRemoveIp(): void {
    ipToRemove = null;
  }

  async function removeIpFromAlias(ip: string): Promise<void> {
    if (!selectedAlias) return;

    try {
      console.log("Removing IP:", ip);
      console.log("Current alias content:", selectedAlias.content);

      const currentContent = selectedAlias.content || "";
      const contentArray = currentContent.split("\n").map((item) => item.trim());
      const updatedContentArray = contentArray.filter((item) => item !== ip);
      const updatedContent = updatedContentArray.join("\n");

      console.log("Updated content:", updatedContent);

      await invoke("remove_ip_from_alias", {
        uuid: selectedAlias.uuid,
        currentContent: updatedContent,
      });

      console.log("Remove IP operation completed, refreshing details");
      await refreshAliasDetails(selectedAlias.name);

      console.log("Refreshed alias details:", selectedAlias);

      if (selectedAlias.content.includes(ip)) {
        throw new Error("IP was not removed successfully");
      }

      toasts.success("IP address removed successfully");
    } catch (err) {
      console.error("Failed to remove IP address:", err);
      toasts.error(
        `Failed to remove IP address: ${err instanceof Error ? err.message : String(err)}`,
      );
    }
  }

  async function refreshAliasDetails(aliasName: string): Promise<void> {
    try {
      console.log("Refreshing alias details for:", aliasName);
      const freshAliasDetails = await invoke<AliasItemsResponse>("search_alias_items");
      console.log("Fresh alias details:", freshAliasDetails);

      if (freshAliasDetails && freshAliasDetails.rows) {
        const freshAlias = freshAliasDetails.rows.find(
          (item) => item.name === aliasName,
        );
        if (freshAlias && selectedAlias) {
          selectedAlias = freshAlias;
          aliasDetails[selectedAlias.name] = freshAlias;
          console.log("Updated selectedAlias:", selectedAlias);
        } else {
          console.error("Couldn't find the updated alias in the fresh data");
        }
      } else {
        console.error("Unexpected format of fresh alias details");
      }
    } catch (err) {
      console.error("Failed to refresh alias details:", err);
      toasts.error(
        `Failed to refresh alias details: ${err instanceof Error ? err.message : String(err)}`,
      );
    }
  }

  function closeModal(): void {
    isModalOpen = false;
    selectedAlias = null;
  }

  async function refreshAliases(): Promise<void> {
    await fetchAliasesAndDetails();
  }

  function handleFilterInput(event: Event): void {
    const target = event.target as HTMLInputElement;
    filter = target.value;
    debouncedApplyFilter();
  }

  function handleKeydown(event: KeyboardEvent): void {
    if (!isModalOpen) {
      const aliasArray = Object.values(filteredAliases);
      if (event.key === "ArrowDown") {
        event.preventDefault();
        selectedIndex = Math.min(selectedIndex + 1, aliasArray.length - 1);
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        selectedIndex = Math.max(selectedIndex - 1, -1);
      } else if (event.key === "Enter" && selectedIndex !== -1) {
        event.preventDefault();
        openAliasDetails(aliasArray[selectedIndex]);
      }
    }
  }

  $: {
    filter;
    if (Object.keys(aliases).length > 0) {
      debouncedApplyFilter();
    }
  }
</script>

<AppLayout>
  <div class="max-w-6xl mx-auto">
    <h2 class="text-2xl font-bold mb-6">Alias List</h2>

    <div class="mb-4 relative">
      <input
        type="text"
        placeholder="Filter aliases"
        class="input input-bordered w-full pl-10"
        on:input={handleFilterInput}
      />
      <svg
        class="w-6 h-6 absolute left-2 top-1/2 transform -translate-y-1/2 text-base-content opacity-60"
        viewBox="0 0 24 24"
      >
        <path fill="currentColor" d={mdiMagnify} />
      </svg>
    </div>

    {#if isLoading}
      <div class="text-center">
        <span class="loading loading-spinner loading-lg"></span>
        <p class="mt-4 text-base-content">Loading aliases...</p>
      </div>
    {:else if error}
      <p class="text-error">Error: {error}</p>
    {:else if Object.keys(filteredAliases).length === 0}
      <p class="text-base-content">No aliases found.</p>
    {:else}
      <div class="space-y-4">
        {#each Object.entries(filteredAliases) as [key, alias], index}
          <div
            class="card bg-base-100 shadow-xl hover:bg-base-200 cursor-pointer transition-colors duration-200"
            class:bg-base-300={index === selectedIndex}
            on:click={() => openAliasDetails(alias)}
          >
            <div class="card-body">
              <h3 class="card-title">{alias.name}</h3>
              <p>{alias.description || "No description assigned."}</p>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>

  <!-- Floating Action Button -->
  <div class="fixed bottom-6 right-6">
    <button
      on:click={refreshAliases}
      class="btn btn-circle btn-lg btn-primary shadow-lg"
      title="Refresh Aliases"
    >
      <svg class="w-6 h-6" viewBox="0 0 24 24">
        <path fill="currentColor" d={mdiRefresh} />
      </svg>
    </button>
  </div>

  <!-- Alias Details Modal -->
  {#if isModalOpen && selectedAlias}
    <div
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
    >
      <div
        class="bg-base-100 rounded-lg shadow-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto"
      >
        <h2 class="text-2xl font-bold mb-4">{selectedAlias.name}</h2>
        <p class="mb-4">
          {selectedAlias.description || "No description assigned."}
        </p>

        <h3 class="text-xl font-semibold mb-2">IP Addresses</h3>
        {#if selectedAlias.content}
          <div class="flex flex-wrap gap-2 mb-4">
            {#each selectedAlias.content.split("\n").map((ip) => ip.trim()) as ip}
              {#if ip}
                <div class="badge badge-lg gap-2 p-3">
                  {ip}
                  <button
                    on:click|stopPropagation={() => showRemoveConfirmation(ip)}
                    class="btn btn-ghost btn-xs p-0 min-h-0 h-auto"
                  >
                    <svg class="w-4 h-4" viewBox="0 0 24 24">
                      <path fill="currentColor" d={mdiClose} />
                    </svg>
                  </button>
                </div>
              {/if}
            {/each}
          </div>
        {:else}
          <p class="mb-4">No IP addresses assigned to this alias.</p>
        {/if}

        <div class="flex items-center mb-4">
          <input
            type="text"
            placeholder="New IP Address"
            class="input input-bordered flex-grow mr-2"
            bind:value={newIpAddress}
          />
          <button
            on:click={addIpToAlias}
            class="btn btn-primary"
            disabled={isAddingIp}
          >
            {#if isAddingIp}
              <span class="loading loading-spinner loading-sm"></span>
            {:else}
              <svg class="w-6 h-6" viewBox="0 0 24 24">
                <path fill="currentColor" d={mdiPlus} />
              </svg>
            {/if}
          </button>
        </div>

        <div class="flex justify-end space-x-2">
          <button on:click={closeModal} class="btn btn-outline">Close</button>
        </div>
      </div>
    </div>
  {/if}

  <!-- Remove IP Confirmation Modal -->
  {#if ipToRemove}
    <div
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-base-100 p-6 rounded-lg">
        <p class="mb-4">Are you sure you want to remove {ipToRemove}?</p>
        <div class="flex justify-end space-x-2">
          <button class="btn btn-outline" on:click={cancelRemoveIp}
            >Cancel</button
          >
          <button class="btn btn-error" on:click={confirmRemoveIp}
            >Remove</button
          >
        </div>
      </div>
    </div>
  {/if}
</AppLayout>

<style>
  .btn-circle {
    @apply rounded-full w-14 h-14 p-0 grid place-items-center;
  }

  .btn-lg {
    @apply w-16 h-16;
  }
</style>
