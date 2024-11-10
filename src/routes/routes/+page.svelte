<script lang="ts">
    import { onMount } from "svelte";
    import { invoke } from "@tauri-apps/api/core";
    import { toasts } from "$lib/stores/toastStore";
    import {
        mdiCheck,
        mdiClose,
        mdiDelete,
        mdiPlus,
        mdiRefresh,
        mdiSelectAll,
        mdiSelectOff,
    } from "@mdi/js";
    import AppLayout from "../AppLayout.svelte";

    interface Route {
        uuid: string;
        disabled: string;
        network: string;
        gateway: string;
        descr: string;
    }

    interface GatewayOption {
        value: string;
        selected: number;
    }

    let routes: (Route & { selected?: boolean })[] = [];
    let isLoading = true;
    let showAddModal = false;
    let showConfirmDelete = false;
    let showConfirmToggle = false;
    let selectedRoute: Route | null = null;
    let gatewayOptions: Record<string, GatewayOption> = {};
    let newRoute = {
        network: "",
        gateway: "",
        description: "",
        disabled: false,
    };
    let selectedAction = "";
    let selectAll = false;
    let isActionLoading = false;

    $: selectedRoutes = routes.filter((route) => route.selected);
    $: hasSelectedRoutes = selectedRoutes.length > 0;

    onMount(async () => {
        await loadRoutes();
        await loadGatewayOptions();
    });

    async function loadRoutes() {
        try {
            const response = await invoke<{ rows: Route[] }>("get_routes");
            routes = response.rows.map((route) => ({
                ...route,
                selected: false,
            }));
            isLoading = false;
        } catch (error) {
            console.error("Failed to load routes:", error);
            toasts.error(`Failed to load routes: ${error}`);
            isLoading = false;
        }
    }

    async function loadGatewayOptions() {
        try {
            const response = await invoke<{
                route: { gateway: Record<string, GatewayOption> };
            }>("get_route_info");
            gatewayOptions = response.route.gateway;
        } catch (error) {
            console.error("Failed to load gateway options:", error);
            toasts.error(`Failed to load gateway options: ${error}`);
        }
    }

    function openAddModal() {
        showAddModal = true;
        newRoute = {
            network: "",
            gateway: "",
            description: "",
            disabled: false,
        };
    }

    function closeAddModal() {
        showAddModal = false;
    }

    async function handleAddRoute() {
        try {
            if (!newRoute.gateway) {
                toasts.error("Please select a gateway");
                return;
            }

            const gatewayName = newRoute.gateway.split(" - ")[0];

            const result = await invoke("add_route", {
                network: newRoute.network,
                gateway: gatewayName,
                description: newRoute.description,
                disabled: newRoute.disabled,
            });

            console.log("Add route result:", result);

            // Automatically apply changes
            await invoke("apply_changes");
            await loadRoutes();
            closeAddModal();
            toasts.success("Route added successfully");
        } catch (error) {
            console.error("Failed to add route:", error);
            toasts.error(`Failed to add route: ${error}`);
        }
    }

    function openDeleteConfirmation(route?: Route) {
        if (route) {
            selectedRoute = route;
        }
        showConfirmDelete = true;
    }

    function closeDeleteConfirmation() {
        showConfirmDelete = false;
        selectedRoute = null;
    }

    function openToggleConfirmation(route?: Route) {
        if (route) {
            selectedRoute = route;
        }
        showConfirmToggle = true;
    }

    function closeToggleConfirmation() {
        showConfirmToggle = false;
        selectedRoute = null;
    }

    async function handleDeleteRoute() {
        try {
            isActionLoading = true;
            if (selectedRoute) {
                await invoke("delete_route", { uuid: selectedRoute.uuid });
            } else if (hasSelectedRoutes) {
                for (const route of selectedRoutes) {
                    await invoke("delete_route", { uuid: route.uuid });
                }
            }

            await invoke("apply_changes");
            await loadRoutes();
            closeDeleteConfirmation();
            toasts.success(
                selectedRoute
                    ? "Route deleted successfully"
                    : "Routes deleted successfully",
            );
        } catch (error) {
            console.error("Failed to delete route(s):", error);
            toasts.error(`Failed to delete route(s): ${error}`);
        } finally {
            isActionLoading = false;
        }
    }

    async function handleToggleRoute() {
        try {
            isActionLoading = true;
            if (selectedRoute) {
                await invoke("toggle_route", { uuid: selectedRoute.uuid });
            } else if (hasSelectedRoutes) {
                for (const route of selectedRoutes) {
                    await invoke("toggle_route", { uuid: route.uuid });
                }
            }

            await invoke("apply_changes");
            await loadRoutes();
            closeToggleConfirmation();
            toasts.success("Route(s) toggled successfully");
        } catch (error) {
            console.error("Failed to toggle route(s):", error);
            toasts.error(`Failed to toggle route(s): ${error}`);
        } finally {
            isActionLoading = false;
        }
    }

    function toggleSelectAll() {
        selectAll = !selectAll;
        routes = routes.map((route) => ({
            ...route,
            selected: selectAll,
        }));
    }
    function handleRouteSelection(route: Route & { selected?: boolean }) {
        route.selected = !route.selected;
        // Update selectAll based on whether all routes are selected
        selectAll = routes.every((r) => r.selected);
    }
    function handleBulkAction() {
        if (!hasSelectedRoutes) return;

        if (selectedAction === "delete") {
            openDeleteConfirmation();
        } else if (selectedAction === "toggle") {
            openToggleConfirmation();
        }

        selectedAction = "";
    }
</script>

<AppLayout>


                {#if isLoading}
                    <div class="flex justify-center items-center h-64">
                        <span class="loading loading-spinner loading-lg"></span>
                    </div>
                {:else}
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body p-0">
                            <!-- Removed default padding for cleaner table look -->
                            <div class="p-4 border-b border-base-200">
                                <!-- Header section with controls -->
                                <div class="flex justify-between items-center">
                                    <h1 class="text-2xl font-bold">
                                        Network Routes
                                    </h1>
                                    <div class="space-x-2 flex items-center">
                                        {#if hasSelectedRoutes}
                                            <select
                                                class="select select-bordered select-sm"
                                                bind:value={selectedAction}
                                                on:change={handleBulkAction}
                                            >
                                                <option value=""
                                                    >Bulk Actions</option
                                                >
                                                <option value="toggle"
                                                    >Toggle Selected</option
                                                >
                                                <option value="delete"
                                                    >Delete Selected</option
                                                >
                                            </select>
                                        {/if}
                                        <button
                                            class="btn btn-sm btn-primary"
                                            on:click={openAddModal}
                                        >
                                            <svg
                                                class="w-5 h-5 mr-2"
                                                viewBox="0 0 24 24"
                                            >
                                                <path
                                                    fill="currentColor"
                                                    d={mdiPlus}
                                                />
                                            </svg>
                                            Add Route
                                        </button>
                                        <button
                                            class="btn btn-sm btn-ghost"
                                            on:click={loadRoutes}
                                            title="Refresh"
                                        >
                                            <svg
                                                class="w-5 h-5"
                                                viewBox="0 0 24 24"
                                            >
                                                <path
                                                    fill="currentColor"
                                                    d={mdiRefresh}
                                                />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div class="overflow-x-auto">
                                <table class="table w-full">
                                    <thead>
                                        <tr class="bg-base-200/50">
                                            <th class="w-10">
                                                <label class="cursor-pointer">
                                                    <input
                                                        type="checkbox"
                                                        class="checkbox checkbox-sm"
                                                        checked={selectAll}
                                                        on:change={toggleSelectAll}
                                                    />
                                                </label>
                                            </th>
                                            <th>Status</th>
                                            <th>Network</th>
                                            <th>Gateway</th>
                                            <th>Description</th>
                                            <th class="text-right">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {#each routes as route}
                                            <tr
                                                class="hover:bg-base-200 border-base-200 transition-colors duration-200 {route.disabled ===
                                                '1'
                                                    ? 'bg-base-200/50 text-base-content/70'
                                                    : ''}"
                                            >
                                                <td>
                                                    <label
                                                        class="cursor-pointer"
                                                    >
                                                        <input
                                                            type="checkbox"
                                                            class="checkbox checkbox-sm"
                                                            bind:checked={route.selected}
                                                            on:change={() =>
                                                                handleRouteSelection(
                                                                    route,
                                                                )}
                                                        />
                                                    </label>
                                                </td>
                                                <td>
                                                    <button
                                                        class="badge badge-{route.disabled ===
                                                        '1'
                                                            ? 'error'
                                                            : 'success'} gap-1 cursor-pointer hover:opacity-80 transition-opacity"
                                                        on:click={() =>
                                                            openToggleConfirmation(
                                                                route,
                                                            )}
                                                        title={route.disabled ===
                                                        "1"
                                                            ? "Click to enable"
                                                            : "Click to disable"}
                                                    >
                                                        <svg
                                                            class="w-3 h-3"
                                                            viewBox="0 0 24 24"
                                                        >
                                                            <path
                                                                fill="currentColor"
                                                                d={route.disabled ===
                                                                "1"
                                                                    ? mdiClose
                                                                    : mdiCheck}
                                                            />
                                                        </svg>
                                                        {route.disabled === "1"
                                                            ? "Disabled"
                                                            : "Enabled"}
                                                    </button>
                                                </td>
                                                <td class="font-mono"
                                                    >{route.network}</td
                                                >
                                                <td class="font-mono"
                                                    >{route.gateway}</td
                                                >
                                                <td>{route.descr || "—"}</td>
                                                <td class="text-right">
                                                    <button
                                                        class="btn btn-ghost btn-sm text-error hover:bg-error/20"
                                                        on:click={() =>
                                                            openDeleteConfirmation(
                                                                route,
                                                            )}
                                                        title="Delete route"
                                                    >
                                                        <svg
                                                            class="w-5 h-5"
                                                            viewBox="0 0 24 24"
                                                        >
                                                            <path
                                                                fill="currentColor"
                                                                d={mdiDelete}
                                                            />
                                                        </svg>
                                                    </button>
                                                </td>
                                            </tr>
                                        {/each}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                {/if}
</AppLayout>

<!-- Add Route Modal -->
{#if showAddModal}
    <div class="modal modal-open">
        <div class="modal-box">
            <h3 class="font-bold text-lg mb-4">Add New Route</h3>
            <form on:submit|preventDefault={handleAddRoute} class="space-y-4">
                <div class="form-control">
                    <label class="label" for="network">
                        <span class="label-text">Network</span>
                    </label>
                    <input
                        type="text"
                        id="network"
                        class="input input-bordered"
                        bind:value={newRoute.network}
                        placeholder="e.g., 192.168.1.0/24"
                        required
                    />
                </div>

                <div class="form-control">
                    <label class="label" for="gateway">
                        <span class="label-text">Gateway</span>
                    </label>
                    <select
                        id="gateway"
                        class="select select-bordered"
                        bind:value={newRoute.gateway}
                        required
                    >
                        <option value="">Select a gateway</option>
                        {#each Object.entries(gatewayOptions) as [key, option]}
                            <option value={option.value}>{option.value}</option>
                        {/each}
                    </select>
                </div>

                <div class="form-control">
                    <label class="label" for="description">
                        <span class="label-text">Description</span>
                    </label>
                    <input
                        type="text"
                        id="description"
                        class="input input-bordered"
                        bind:value={newRoute.description}
                        placeholder="Route description"
                    />
                </div>

                <div class="form-control">
                    <label class="label cursor-pointer">
                        <span class="label-text">Disabled</span>
                        <input
                            type="checkbox"
                            class="toggle"
                            bind:checked={newRoute.disabled}
                        />
                    </label>
                </div>

                <div class="modal-action">
                    <button type="button" class="btn" on:click={closeAddModal}
                        >Cancel</button
                    >
                    <button type="submit" class="btn btn-primary"
                        >Add Route</button
                    >
                </div>
            </form>
        </div>
    </div>
{/if}

<!-- Delete Confirmation Modal -->
{#if showConfirmDelete}
    <div class="modal modal-open">
        <div class="modal-box">
            <h3 class="font-bold text-lg">Confirm Delete</h3>
            <p class="py-4">
                {#if selectedRoute}
                    Are you sure you want to delete the route to {selectedRoute.network}?
                {:else}
                    Are you sure you want to delete {selectedRoutes.length} selected
                    routes?
                {/if}
                This action cannot be undone.
            </p>
            <div class="modal-action">
                <button
                    class="btn"
                    on:click={closeDeleteConfirmation}
                    disabled={isActionLoading}
                >
                    Cancel
                </button>
                <button
                    class="btn btn-error {isActionLoading ? 'loading' : ''}"
                    on:click={handleDeleteRoute}
                    disabled={isActionLoading}
                >
                    Delete
                </button>
            </div>
        </div>
    </div>
{/if}

<!-- Toggle Confirmation Modal -->
{#if showConfirmToggle}
    <div class="modal modal-open">
        <div class="modal-box">
            <h3 class="font-bold text-lg">Confirm Toggle</h3>
            <p class="py-4">
                {#if selectedRoute}
                    Are you sure you want to {selectedRoute.disabled === "1"
                        ? "enable"
                        : "disable"} the route to {selectedRoute.network}?
                {:else}
                    Are you sure you want to toggle {selectedRoutes.length} selected
                    routes?
                {/if}
            </p>
            <div class="modal-action">
                <button
                    class="btn"
                    on:click={closeToggleConfirmation}
                    disabled={isActionLoading}
                >
                    Cancel
                </button>
                <button
                    class="btn btn-primary {isActionLoading ? 'loading' : ''}"
                    on:click={handleToggleRoute}
                    disabled={isActionLoading}
                >
                    Continue
                </button>
            </div>
        </div>
    </div>
{/if}
