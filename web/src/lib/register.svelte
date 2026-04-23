<script lang="ts">
  import Search from "$lib/multiselect.svelte";
  import AllJobRoles from "$lib/job_roles.json";
  import { set } from "valibot";
  import { goto } from "$app/navigation";
  import { supabase } from "$lib/supabaseClient";
  import { onMount } from "svelte";

  let name = $state("");
  let file: Blob | string = $state("");
  const setFile = (d: Blob | string) => (file = d);
  let allJobRoles = $state(AllJobRoles.sort((a: string, b: string) => a.localeCompare(b)));
  let jobRoles: string[] = $state([]);
  let stepNum = $state(1);
  let profile = $state({
    id: "",
    email_id: "",
    full_name: "",
    preferred_role_1: "",
    preferred_role_2: "",
    preferred_role_3: "",
    resume_url: ""
  });


  onMount(async () => {
    const { data: userData, error: userErr } = await supabase.auth.getUser();
    if (!userErr) {
      profile.id = userData.user?.id || "";
      profile.email_id = userData.user?.email || "";
    }
    const { data, error } = await supabase.from("profiles").select("*").single();
    //console.log("Supabase profile fetch response:", { data, error });
  });

  const setSelectedJobs = (d: string[]) => {
    jobRoles = d;
  };
  const setStepNum = (next: boolean) => {
    if (next) {
      stepNum += 1;
    } else {
      stepNum -= 1;
    }
  };

  const uploadResume = async (e: Event) => {
    setFile((e.target as HTMLInputElement).files?.[0] ?? "");
    const filePath = `${profile.id}/resume.pdf`;
    const { data: fileData, error: fileErr } = await supabase.storage.from("resumes").upload(filePath, file, {upsert: true});

    if (!fileErr) {
      profile.resume_url = filePath;
      return fileData;
    }
    console.error("Error uploading file:", fileErr);
    return "";
  };

  const handleSubmit = async () => {
    profile.full_name = name;
    profile.preferred_role_1 = jobRoles[0] ?? "";
    profile.preferred_role_2 = jobRoles[1] ?? "";
    profile.preferred_role_3 = jobRoles[2] ?? "";
    //console.log("Profile info to be inserted:", profile);

    try {
      const profileUp = await supabase.from('profiles').upsert(profile).select();
      //console.log("Supabase profile upsert response:", profileUp);
      goto("/");
    } catch (err) {
      console.error("Error during profile upsert:", err);
    }
    
  };
  const unselected = "[border:1px_solid_black]  bg-white rounded-4px px-12px py-4px";
  const selected = "bg-black text-white rounded-4px px-12px py-4px";

  const { setJobRoles } = $props();
</script>

<div class="w-1/3 max-w-[600px] flex flex-col mt-80px mx-auto gap-40px">
  <div>
    <h1 class="text-[24px] font-bold">Profile Set-Up</h1>
    <div class="flex flex-row items-center justify-center content-center gap-12px mt-16px">
      <div class="{stepNum === 1 ? selected : unselected}">
        1. Resume
      </div>
      <box class="w-40px h-2px bg-black"></box>
      <div class="{stepNum === 2 ? selected : unselected}">
        2. Name
      </div>
      <box class="w-40px h-2px bg-black"></box>
      <div class="{stepNum === 3 ? selected : unselected}">
        3. Job Roles
      </div>
    </div>
  </div>
  <form>
    {#if stepNum === 1}
    <div class="my-4px">
      <p class="font-600">Upload resume</p>
      <input
        class="mt-8px [border:1px_solid_#DADADA] rounded-md px-12px py-2 w-full"
        type="file"
        accept=".pdf"
        required
        onchange={(e) => uploadResume(e)}
      />
    </div>
    {:else if stepNum === 2}
    <div class="items-center flex flex-col">
      <p>Name: </p>
      <textarea class="rounded-4px [border:1px_solid_#DADADA] resize-none px-4px"
        rows="1" required bind:value={name}></textarea>
    </div>
    {:else if stepNum === 3}
    <div>
      <div class="mb-12px">
        <p class="font-600">Job Role Preferences</p>
        <p class="font-400">Please select up to 3 preferences for your job search</p>
          <Search
            selected={jobRoles}
            data={allJobRoles}
            setData={setJobRoles}
            setSelected={setSelectedJobs}
            editing={false} />
        <ul class="flex mt-8px gap-12px flex-row flex-wrap">
          {#each jobRoles as role}
          <!-- Change each to for, number each job role -->
            <li class="rounded-6px [border:2px_solid_#000000] resize-none p-4px flex items-center">
              {role}
            </li>
          {/each}
        </ul>
      </div>
    </div>
    {/if}
  <div class="flex justify-between mt-[16px]">
    {#if stepNum === 1}
      <button class="bg-black rounded-6px px-12px py-4px h-[32px]"
      onclick={() => goto("/")}>
        <h3 class="text-white">Back to Login</h3>
      </button>
    {:else}
      <button class="bg-black rounded-6px px-12px py-4px h-[32px]"
      onclick={() => setStepNum(false)}>
        <h3 class="text-white">Back</h3>
      </button>
    {/if}
    {#if stepNum === 3}
      <button class="bg-black rounded-6px px-12px py-4px h-[32px]"
      onclick={() => handleSubmit()}>
        <h3 class="text-white">Finish</h3>
      </button>
    {:else}
      {#if (stepNum === 2 && name == "") || (stepNum === 1 && file == "") || (stepNum === 3 && jobRoles.length == 0)}
        <button class="bg-[#D9D9D9] rounded-6px px-12px py-4px h-[32px]"
        disabled onclick={() => setStepNum(true)}>
          <h3 class="text-[#FAFAFA]">Next</h3>
        </button>
      {:else}
        <button class="bg-black rounded-6px px-12px py-4px h-[32px]"
        onclick={() => setStepNum(true)}>
          <h3 class="text-white">Next</h3>
        </button>
      {/if}
    {/if}
  </div>
  </form>
</div>