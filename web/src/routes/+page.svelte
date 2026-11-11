<script lang="ts">
  import { supabase } from "$lib/supabaseClient.js";
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import type { AuthSession } from "@supabase/supabase-js";
  import Login from "$lib/login.svelte";
  import Homepage from "../Homepage.svelte";
  import NavBar from "$lib/nav_bar.svelte";

  let { data } = $props();
  let profile: any = $state(null);
  let session = $state<AuthSession | null>(null);
  let loading = $state(true);

  const resolveUser = async (s: AuthSession | null) => {
    // Skip if nothing changed
    if (s?.user.id && s.user.id === session?.user.id && profile) return;

    session = s;
    if (!s) {
      profile = null;
      loading = false;
      return;
    }

    loading = true;
    const { data: p, error } = await supabase
      .from("profiles").select("*").eq("id", s.user.id).maybeSingle();

    if (error) {
      console.error("Error fetching profile:", error);
      loading = false;          // shows the error branch below
      return;
    }
    if (!p) {
      // Keep the loading state up and go straight to registration for new users
      await goto("/registration", { replaceState: true });
      return;
    }
    profile = p;
    loading = false;
  };

  onMount(() => {
    supabase.auth.getSession().then(({ data }) => resolveUser(data.session));

    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, s) => {
      if (event === "SIGNED_IN" || event === "SIGNED_OUT") {
        setTimeout(() => resolveUser(s), 0);
      }
    });
    return () => subscription.unsubscribe();
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
    {:else if session && profile}
      <NavBar loggedIn={session} profileName={profile.full_name || ""} />
      <Homepage {profile}
        defaultJobListings={data.defaultJobListings}
        sessionID={data.sessionID}
      />
    {:else if session}
      <NavBar loggedIn={true} />
      <p class="text-center mt-48px">Couldn't load profile. Please refresh.</p>
    {:else}
      <NavBar loggedIn={session} />
      <Login sessionID={data.sessionID}/>
  {/if}
</div>
