<script lang="ts">
  import Login from "$lib/login.svelte";
  import Homepage from "../Homepage.svelte";

  let { data } = $props();
</script>

{#if data.isAuthed}
  <Homepage
    defaultJobListings={data.defaultJobListings}
    sessionID={data.sessionID}
  />
{:else}
  <Login />
{/if}
