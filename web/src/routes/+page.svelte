<script lang="ts">
  import { QueryClient, QueryClientProvider } from "@tanstack/svelte-query";

  import Login from "$lib/login.svelte";
  import Homepage from "../Homepage.svelte";

  let { data } = $props();

  const queryClient = new QueryClient();
</script>

<QueryClientProvider client={queryClient}>
  {#if data.isAuthed}
    <Homepage
      defaultJobListings={data.defaultJobListings}
      sessionID={data.sessionID}
    />
  {:else}
    <Login />
  {/if}
</QueryClientProvider>
