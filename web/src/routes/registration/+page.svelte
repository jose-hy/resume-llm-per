<script lang="ts">
  import { supabase } from "$lib/supabaseClient.js";
  import { onMount } from "svelte";
  import type { AuthSession } from "@supabase/supabase-js";

  import NavBar from "$lib/nav_bar.svelte";
  import Register from "$lib/register.svelte";

  let jobRoles: string[] = $state([]);
  const setJobRoles = (d: string[]) => {
    jobRoles = d;
  };

  let { data } = $props();
  let session = $state<AuthSession | null>(null);
  let loading = $state(true);
  

  onMount(async () => {
    supabase.auth.getSession().then(({data}) => {
      session = data.session;
      loading = false;
    })

    supabase.auth.onAuthStateChange((_event, _session) => {
      session = _session;
    });
  });
</script>

<div>
  <NavBar loggedIn={false} />
  <Register setJobRoles={setJobRoles} />
</div>