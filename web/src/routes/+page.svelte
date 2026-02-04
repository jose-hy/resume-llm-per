<script lang="ts">
  import Login from "$lib/login.svelte";
  import Homepage from "../Homepage.svelte";
  import NavBar from "$lib/nav_bar.svelte";

  let { data } = $props();
</script>

<div>
  {#if data.isAuthed}
    <NavBar loggedIn={true} />
    <Homepage
      defaultJobListings={data.defaultJobListings}
      sessionID={data.sessionID}
    />
  {:else}
    <NavBar loggedIn={false} />
    <Login />
  {/if}
</div>
