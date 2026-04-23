<script lang="ts">
  import { supabase } from "$lib/supabaseClient.js";
  import { onMount } from "svelte";
  import type { AuthSession } from "@supabase/supabase-js";
  import Login from "$lib/login.svelte";
  import Homepage from "../Homepage.svelte";
  import NavBar from "$lib/nav_bar.svelte";

  let { data } = $props();
  let userProfile = $state("");
  let session = $state<AuthSession | null>(null);
  let loading = $state(true);

  onMount(async () => {
    supabase.auth.getSession().then(({data}) => {
      session = data.session;
      loading = false;
    });

    supabase.auth.onAuthStateChange((_event, _session) => {
      session = _session;
    });

    try {
      const { data: profile, error } = await supabase.from("profiles").select("*").single();
    if (profile) {
      userProfile = profile.full_name || "";
    }
    } catch (error) {
      console.error("Error fetching user profile:", error);
    };
    
  });
</script>

<div>
  {#if loading}
    <NavBar loggedIn={false} />
    <div class="flex justify-center items-center min-h-screen gap-16px">
      <div class="border-t-[gray] border-l-[gray] border-b-[gray]
        w-[16px] h-[16px] border-[2px] border-transparent
        spinner animate-spin rounded-circle"></div>
      <span class="text-lg text-gray-500">Loading...</span>
    </div>
  {:else}
    {#if session}
      <NavBar loggedIn={session} profileName={userProfile} />
      <Homepage
        defaultJobListings={data.defaultJobListings}
        sessionID={data.sessionID}
      />
    {:else}
      <NavBar loggedIn={session} />
      <Login sessionID={data.sessionID}/>
    {/if}
  {/if}
</div>
