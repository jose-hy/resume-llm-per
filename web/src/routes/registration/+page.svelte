<script lang="ts">
  import NavBar from "$lib/nav_bar.svelte";
  import Register from "$lib/register.svelte";

  let jobRoles: string[] = $state([]);
  const setJobRoles = (d: string[]) => {
    jobRoles = d;
  };

  let { data } = $props();
</script>

<div>
  <NavBar loggedIn={false} />
  <Register setJobRoles={setJobRoles} />
</div>