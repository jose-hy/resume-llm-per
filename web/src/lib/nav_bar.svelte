<script lang="ts">
  import { get, post } from "../utils";
  import { goto, invalidateAll } from "$app/navigation";
  import { supabase } from "./supabaseClient.js";
  import Avatar from "./profile_pic.svelte";

  const {
    loggedIn,
    profileName = "User"
  } = $props();

  const homeClick = async () => {
    if (loggedIn) {
      await goto("/");
    };
  }

  const logout = async () => {
    {/*if (window.location.pathname !== "/") {
      await goto("/");
    }
    await get("/logout_user");*/}
    const { error } = await supabase.auth.signOut({ scope: 'local' });
    if (error) {
      console.error("Error signing out:", error);
    } 
    //console.log("Successfully signed out");
    await goto("/");
    invalidateAll();
  };

  let clicked = $state(false);
  const handleProfileClick = () => {
    clicked = !clicked;
  };
  /**
   * <li class="text-white hover:text-black hover:bg-white px-8px py-4px hover:rounded-[4px]"> 
      <button type="button" onclick={() => goto("/registration")}>Register Page</button> </li>
   */

</script>

<div class=" flex bg-black ">
  <nav class="flex justify-between items-center w-full px-16px py-12px">
    <div class="text-center flex flex-col text-[24px]">
      <button type="button" onclick={() => {
        homeClick()} 
      }>
        <h1 class="text-white font-extrabold m-0">Interview</h1>
        <h1 class="text-white font-extrabold m-0 -mt-4">Moves</h1>
      </button>
    </div>
    <div class="flex gap-20px items-center">
      {#if !loggedIn}
        <button type="button"><h3 class="text-white">Log In/Sign Up</h3></button>
      {:else}
        <ul class="flex gap-12px flex-row-reverse justify-center items-center">
          <li>
            <button type="button" onclick={handleProfileClick} class="mt-[6px]">
              <Avatar round={false} userFullName={profileName} width={32} />
            </button>
          </li>
          {#if clicked}
          <li class="text-white hover:text-black hover:bg-white px-8px py-4px hover:rounded-[4px]">
            <button type="button" onclick={() => goto("/profile")}>Profile</button> </li>
          <li class="text-white hover:text-black hover:bg-white px-8px py-4px hover:rounded-[4px]">
            <button type="button" onclick={logout}>Sign Out</button> </li>
          {/if}
        </ul>
      {/if}
    </div>
  </nav>
</div>