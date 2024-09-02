import { writable } from 'svelte/store';

export const fabStore = writable({
    isExpanded: false
});

export function toggleFab() {
    fabStore.update(state => ({ isExpanded: !state.isExpanded }));
}

export function closeFab() {
    fabStore.set({ isExpanded: false });
}