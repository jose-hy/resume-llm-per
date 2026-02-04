<script lang="ts">
  import NavBar from "$lib/nav_bar.svelte";
  import Profile from "$lib/profile.svelte";
  import Applied from "$lib/applied_jobs.svelte";

  let jobRoles: string[] = $state([]);
  const setJobRoles = (d: string[]) => {
    jobRoles = d;
  };

  let { data } = $props();

</script>

<div class="min-h-screen flex flex-col">
    <NavBar loggedIn={true} />
    <div class="flex flex-row mx-auto p-20px gap-40px">
      <Profile setJobRoles={setJobRoles} />
      <Applied 
      defaultJobListings={data.defaultJobListings}
      sessionID={data.sessionID} />
    </div>
</div>