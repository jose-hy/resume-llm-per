<script lang="ts">
  import { supabase } from "$lib/supabaseClient.js";
  import { onMount } from "svelte";
  import type { Session } from "@supabase/supabase-js";
  import NavBar from "$lib/nav_bar.svelte";
  import Profile from "$lib/profile.svelte";
  import Applied from "$lib/applied_jobs.svelte";

  let jobRoles: string[] = $state([]);
  const setJobRoles = (d: string[]) => {
    jobRoles = d;
  };

  let { data } = $props();
  let sessionData: { session: Session | null } = $state({ session: null });
  let userProfile = $state("");
  let profileUser: any = $state(null);
  let auth = $state(false);
  let authListener;
  let userID = $state("");

  const checkAuth = async () => {
    const { data: session , error } = await supabase.auth.getSession();
    sessionData = session;
    //console.log("Supabase getSession response:", session);
    if (error) {
      console.error("Error checking auth:", error);
      return false;
    }
    return !!session;
  };

  onMount(async () => {
    auth = await checkAuth();

    authListener = supabase.auth.onAuthStateChange(async (_event, _session) => {
      auth = await checkAuth();
    });

    const { data: profile, error } = await supabase.from("profiles").select("*").single();
    userProfile = profile.full_name || "";
    profileUser = profile;
    userID = profile.id;
  });

</script>

<div class="min-h-screen flex flex-col">
    <NavBar 
    loggedIn={true}
    profileName={userProfile} />
    <div class="flex flex-row mx-auto p-20px gap-40px">
      {#if profileUser}
      <Profile 
      profile={profileUser}
      uID={userID}
      setJobRoles={setJobRoles} />
      {/if}
      {#if userID}
      <Applied 
      defaultJobListings={data.defaultJobListings}
      userID={userID}
      sessionID={data.sessionID} />
      {/if}
    </div>
</div>