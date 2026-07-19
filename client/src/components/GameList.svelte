<script lang="ts">
    import { onMount } from "svelte";
    import GameCard from "./GameCard.svelte";
    import LoadingSkeleton from "./LoadingSkeleton.svelte";
    import ErrorMessage from "./ErrorMessage.svelte";
    import EmptyState from "./EmptyState.svelte";
    import type { Game, Publisher, Category } from "../types/game";

    let { initialGames = [] }: { initialGames?: Game[] } = $props();
    let games = $state<Game[]>(initialGames);
    let publishers = $state<Publisher[]>([]);
    let categories = $state<Category[]>([]);
    let loading = $state(true);
    let error = $state<string | null>(null);
    let selectedPublisherId = $state<string>("all");
    let selectedCategoryId = $state<string>("all");

    let hasActiveFilters = $derived(
        selectedPublisherId !== "all" || selectedCategoryId !== "all"
    );

    let filteredGames = $derived(
        games.filter((game) => {
            const publisherMatches =
                selectedPublisherId === "all" || game.publisher?.id === Number(selectedPublisherId);
            const categoryMatches =
                selectedCategoryId === "all" || game.category?.id === Number(selectedCategoryId);
            return publisherMatches && categoryMatches;
        })
    );

    const resetFilters = (): void => {
        selectedPublisherId = "all";
        selectedCategoryId = "all";
    };

    const fetchCatalogData = async (): Promise<void> => {
        loading = true;
        error = null;
        try {
            const [gamesResponse, publishersResponse, categoriesResponse] = await Promise.all([
                fetch('/api/games'),
                fetch('/api/publishers'),
                fetch('/api/categories')
            ]);

            if (!gamesResponse.ok || !publishersResponse.ok || !categoriesResponse.ok) {
                const responseErrors = [
                    !gamesResponse.ok ? `games (${gamesResponse.status})` : null,
                    !publishersResponse.ok ? `publishers (${publishersResponse.status})` : null,
                    !categoriesResponse.ok ? `categories (${categoriesResponse.status})` : null
                ].filter(Boolean).join(', ');

                error = `Failed to fetch API data for: ${responseErrors}`;
                return;
            }

            const [gamesData, publishersData, categoriesData] = await Promise.all([
                gamesResponse.json() as Promise<Game[]>,
                publishersResponse.json() as Promise<Publisher[]>,
                categoriesResponse.json() as Promise<Category[]>
            ]);

            games = gamesData;
            publishers = publishersData;
            categories = categoriesData;
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };

    onMount(() => {
        fetchCatalogData();
    });
</script>

<div>
    <h2 class="text-2xl font-medium mb-6 text-slate-100">Featured Games</h2>
    
    {#if loading}
        <LoadingSkeleton count={6} />
    {:else if error}
        <ErrorMessage error={error} />
    {:else}
        <div class="mb-6 bg-slate-800/50 border border-slate-700 rounded-xl p-4" data-testid="game-filter-controls">
            <div class="flex flex-col md:flex-row gap-4 items-start md:items-end">
                <div class="w-full md:w-auto flex-1">
                    <label for="publisher-filter" class="block text-sm font-medium text-slate-200 mb-2">Publisher</label>
                    <select
                        id="publisher-filter"
                        class="w-full bg-slate-900 border border-slate-600 text-slate-100 rounded-lg p-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={selectedPublisherId}
                        onchange={(event) => {
                            selectedPublisherId = (event.currentTarget as HTMLSelectElement).value;
                        }}
                        data-testid="publisher-filter"
                    >
                        <option value="all">All publishers</option>
                        {#each publishers as publisher (publisher.id)}
                            <option value={String(publisher.id)}>{publisher.name}</option>
                        {/each}
                    </select>
                </div>

                <div class="w-full md:w-auto flex-1">
                    <label for="category-filter" class="block text-sm font-medium text-slate-200 mb-2">Category</label>
                    <select
                        id="category-filter"
                        class="w-full bg-slate-900 border border-slate-600 text-slate-100 rounded-lg p-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={selectedCategoryId}
                        onchange={(event) => {
                            selectedCategoryId = (event.currentTarget as HTMLSelectElement).value;
                        }}
                        data-testid="category-filter"
                    >
                        <option value="all">All categories</option>
                        {#each categories as category (category.id)}
                            <option value={String(category.id)}>{category.name}</option>
                        {/each}
                    </select>
                </div>

                <button
                    type="button"
                    class="w-full md:w-auto bg-slate-700 hover:bg-slate-600 text-slate-100 rounded-lg px-4 py-2.5 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    onclick={resetFilters}
                    disabled={!hasActiveFilters}
                    data-testid="clear-filters-button"
                >
                    Clear filters
                </button>
            </div>
        </div>

        {#if filteredGames.length === 0}
            <EmptyState message={hasActiveFilters ? "No games match the selected filters." : "No games available at the moment."} />
        {:else}
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="games-grid">
            {#each filteredGames as game (game.id)}
                <GameCard {game} />
            {/each}
        </div>
        {/if}
    {/if}
</div>