<script lang="ts">
  import Avatar from "$lib/profile_pic.svelte";
  import Search from "$lib/multiselect.svelte";

  import AllJobRoles from "$lib/job_roles.json";
  import { onMount } from "svelte";
  import { supabase } from "./supabaseClient";

  const { uID, profile, setJobRoles } = $props();

  let name = $state("");
  let bio = $state("Add a short bio about yourself.");
  let fileName: string | undefined = $state("");
  let file: Blob | string = $state("");
  const setFile = (d: Blob | string) => (file = d);

  let allJobRoles = $state(AllJobRoles.sort((a: string, b: string) => a.localeCompare(b)));
  let jobRoles = $state([""]);

  let editName = $state("");
  let editFileName: string | undefined = $state("");
  let editFile: Blob | string = $state("");
  let setEditFile = (d: Blob | string) => (editFile = d);
  let editJobs = $state([""]);

  let editing = $state(false);

  onMount( async () => {
    name = profile?.full_name || "";
    jobRoles = [profile?.preferred_role_1, profile?.preferred_role_2, profile?.preferred_role_3];

    fileName = profile?.resume_url.split("/")[1] || "";
    const url = await supabase.storage.from("resumes").createSignedUrl(`${profile.resume_url}`, 60);
    setFile(url.data?.signedUrl || "");

    editName = name;
    editJobs = removeEmpty(jobRoles);
    setEditFile(url.data?.signedUrl || "");
  });

  const removeEmpty = (jobArr: string[]) => {
    return jobArr.filter((job) => job !== "" && job !== null && job !== undefined);
  };

  const handleEdit = () => {
    editing = !editing;
    // Make all edit values back to default values
    editName = name;
    editJobs = removeEmpty(jobRoles);
    setEditFile(file);
    editFileName = fileName;
  };

  const handleResume = async (e: Event) => {
    setEditFile((e.target as HTMLInputElement).files?.[0] ?? "");
    editFileName = (e.target as HTMLInputElement).files?.[0].name;
  }

  const setSelectedJobs = (d: string[]) => {
    editJobs = d;
  };

  const handleSubmit = async () => {
    // Create object of changed values to update profile info
    let updateFields = {};
    if (editName !== name) {
      updateFields = {...updateFields, full_name: editName};
    }
    if (editJobs !== jobRoles) {
      updateFields = {
        ...updateFields,
        preferred_role_1: editJobs[0] || "",
        preferred_role_2: editJobs[1] || "",
        preferred_role_3: editJobs[2] || "",
      };
    }

    // Upload new resume to storage
    if (editFile !== file) {
      const filePath = `${uID}/resume.pdf`;
      const { data: fileData, error: fileErr } = await supabase.storage.from("resumes").upload(filePath, editFile, {upsert: true});
      if (!fileErr) {
        updateFields = {...updateFields, resume_url: filePath};
        fileName = filePath.split("/")[1];
      }
    }

    // Call API to update profile information
    if (Object.keys(updateFields).length > 0) {
      const { error } = await supabase.from("profiles").update(updateFields).eq("id", uID);
      //console.log("Supabase profile update response:", error ?? "Profile updated successfully");

      // Make all edit values the new default values after successful update
      name = editName;
      jobRoles = editJobs;
      fileName = editFileName;
      setFile(editFile);
      
      editing = !editing;
      return true;
    }
    editing = !editing;
    return false;
  };

</script>

<div class="w-1/3 gap-20px flex flex-col max-w-[600px] min-w-[400px]">
  <div class="flex flex-row relative gap-20px">
    <div class="flex flex-col gap-8px w-full">
    {#if editing}
      <label for="editName" class="font-600">Name</label>
      <textarea class="w-full rounded-4px [border:1px_solid_#DADADA] resize-none px-4px"
        rows="1" bind:value={editName} id="editName"></textarea>
    {:else}
      <h1 class="font-bold text-2xl">{editName}</h1>
    {/if}
    </div>
  </div>
  <div class="my-4px">
    <p class="font-600">Resume</p>
    {#if editing}
    <input
      class="mt-8px [border:1px_solid_#DADADA] rounded-md px-12px py-2 w-full"
      type="file"
      accept=".pdf"
      disabled={!editing}
      onchange={(e) => handleResume(e)}
    />
    {:else}
    <a href={file.toString()} target="_blank" class="text-blue-600 underline">{fileName}</a>
    {/if}
  </div>
  <div class="mb-12px">
    <p class="font-600">Job Role Preferences</p>
    {#if editing}
      <Search
        selected={editJobs}
        data={allJobRoles}
        setData={setJobRoles}
        setSelected={setSelectedJobs}
        editing={true} />
    {/if}
    {#if !editing}
    <ul class="flex mt-8px gap-12px flex-row flex-wrap">
      {#each editJobs as role}
      <!-- Change from each to for: Number the job role -->
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
        onclick={handleSubmit}>
        Save Changes
      </button>
      <button type="button" class="[border:1px_solid_black] rounded-4px px-12px py-4px"
        onclick={handleEdit}>
        Cancel
      </button>
    </div>
    {:else}
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
  {/if}
</div>