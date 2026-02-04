<script lang="ts">
  import Avatar from "$lib/profile_pic.svelte";
  import Search from "$lib/multiselect.svelte";

  import AllJobRoles from "$lib/job_roles.json";

  const { setJobRoles } = $props();

  let name = $state("Firstname Lastname");
  let bio = $state("Short bio describing background and experience. Can be edited and saved.");
  let file: Blob | string = $state("");
  const setFile = (d: Blob | string) => (file = d);
  let editing = $state(false);

  const handleEdit = () => {
    editing = !editing;
  }

  let allJobRoles = $state(AllJobRoles.sort((a: string, b: string) => a.localeCompare(b)));
  let jobRoles = $state([ "IT Associate", "IT Support Specialist", "Network Technician"]);

  const setSelectedJobs = (d: string[]) => {
    jobRoles = d;
  };

</script>

<div class="w-1/3 gap-20px flex flex-col max-w-[600px]">
  <div class="flex flex-row relative gap-20px mb-16px">
    <span class="max-h-[96px] min-w-[96px]" >
    <Avatar round={false} width={96} userFullName={name} />
    </span>
    <div class="flex flex-col gap-8px w-full">
    {#if editing}
      <textarea class="w-full rounded-4px [border:1px_solid_#DADADA] resize-none px-4px"
        rows="1" bind:value={name}></textarea>
      <textarea class="w-full rounded-4px [border:1px_solid_#DADADA] resize-none px-4px py-4px"
        rows="2" bind:value={bio}></textarea>
    {:else}
      <h1 class="px-4px bold">{name}</h1>
      <p class="px-4px py-8px w-full">{bio}</p>
    {/if}
    </div>
  </div>
  <div class="flex mt-[-8px] mb-12px">
    <button type="button" onclick={handleEdit}
      class="bg-black text-white rounded-6px px-12px py-4px h-[32px]">
        {#if editing}
          Editing Profile
        {:else}
          Edit Profile
        {/if}
        
      </button>
    </div>
  <div class="my-4px">
    <p class="font-600">Upload resume</p>
    <input
      class="mt-8px [border:1px_solid_#DADADA] rounded-md px-12px py-2 w-full"
      type="file"
      disabled={!editing}
      onchange={(e) => setFile((e.target as HTMLInputElement).files?.[0] ?? "")}
    />
  </div>
  <div class="mb-12px">
    <p class="font-600">Job Role Preferences</p>
    {#if editing}
      <Search
        selected={jobRoles}
        data={allJobRoles}
        setData={setJobRoles}
        setSelected={setSelectedJobs}
        editing={true} />
    {/if}
    {#if !editing}
    <ul class="flex mt-8px gap-12px flex-row flex-wrap">
      {#each jobRoles as role}
        <li class="rounded-6px [border:2px_solid_#000000] resize-none p-4px flex items-center">
          {role}
        </li>
      {/each}
    </ul>
    {/if}
  </div>
  {#if editing}
    <div>
      <button type="button" class="bg-black text-white rounded-6px px-12px py-4px h-32px"
        onclick={handleEdit}>
        Save Changes
      </button>
      <button type="button" class="[border:1px_solid_black] rounded-4px px-12px py-4px"
        onclick={handleEdit}>
        Cancel
      </button>
    </div>
  {/if}
</div>