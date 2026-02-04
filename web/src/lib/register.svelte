<script lang="ts">
  import Search from "$lib/multiselect.svelte";
  import AllJobRoles from "$lib/job_roles.json";
    import { set } from "valibot";
    import { goto } from "$app/navigation";

  let firstName = $state("");
  let lastName = $state("");
  let name = $derived(`${firstName} ${lastName}`);
  let file: Blob | string = $state("");
  const setFile = (d: Blob | string) => (file = d);
  let allJobRoles = $state(AllJobRoles.sort((a: string, b: string) => a.localeCompare(b)));
  let jobRoles: string[] = $state([]);
  let stepNum = $state(1);

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

  const { setJobRoles } = $props();
</script>

<div class="w-1/3 max-w-[600px] flex flex-col mt-80px mx-auto gap-40px">
  {#if stepNum === 1}
  <div class="my-4px">
    <p class="font-600">Upload resume</p>
    <input
      class="mt-8px [border:1px_solid_#DADADA] rounded-md px-12px py-2 w-full"
      type="file"
      onchange={(e) => setFile((e.target as HTMLInputElement).files?.[0] ?? "")}
    />
  </div>
  {:else if stepNum === 2}
  <div class="items-center flex flex-col">
    <p>First Name: </p>
    <textarea class="rounded-4px [border:1px_solid_#DADADA] resize-none px-4px"
      rows="1" bind:value={firstName}></textarea>
    <p>Last Name: </p>
    <textarea class="rounded-4px [border:1px_solid_#DADADA] resize-none px-4px"
      rows="1" bind:value={lastName}></textarea>
  </div>
  {:else if stepNum === 3}
  <div>
    <div class="mb-12px">
      <p class="font-600">Job Role Preferences</p>
        <Search
          selected={jobRoles}
          data={allJobRoles}
          setData={setJobRoles}
          setSelected={setSelectedJobs}
          editing={false} />
      <ul class="flex mt-8px gap-12px flex-row flex-wrap">
        {#each jobRoles as role}
          <li class="rounded-6px [border:2px_solid_#000000] resize-none p-4px flex items-center">
            {role}
          </li>
        {/each}
      </ul>
    </div>
  </div>
  {/if}
  <div class="flex justify-between">
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
      onclick={() => goto("/")}>
        <h3 class="text-white">Finish</h3>
      </button>
    {:else}
      {#if stepNum === 2 && (firstName == "" || lastName == "")}
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
</div>