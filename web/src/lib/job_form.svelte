<script lang="ts">
  import Search from "$lib/multiselect.svelte";
  import { onMount } from "svelte";
  import Spacer from "./spacer.svelte";
  import { get, stateAbbreviations } from "../utils";

  import { store } from "./store.svelte";

  let isLoading = $state(false);
  const degreeRequirements = ["No degree", "Required"];

  const employmentType = ["Part-time", "Full-time", "Contract", "Internship"];

  onMount(async () => {
    const res = await get("/analytics");
    const data = await res.json();
    console.log(data);
  });
</script>

<div
  class="bg-white [border:1px_solid_#DADADA] rounded-8px w-[400px] sticky top-24px px-24px py-32px"
>
  <p>This app matches your resume with job openings in the IT field.</p>
  <Spacer axis="y" size="24" />
  <p class="font-600">Upload resume</p>
  <input
    class="[border:1px_solid_black] rounded-4px px-12px py-4px"
    type="file"
    onchange={(e) =>
      store.setFile((e.target as HTMLInputElement).files?.[0] ?? "")}
  />
  <Spacer axis="y" size="24" />
  <p class="font-600">Locations</p>
  <Search
    data={["All", ...Object.keys(stateAbbreviations)]}
    setData={store.setLocations}
  />
  <Spacer axis="y" size="24" />
  <p class="font-600">Degree requirements</p>
  <Search data={degreeRequirements} setData={store.setDegreeRequirements} />
  <Spacer axis="y" size="24" />
  <p class="font-600">Employment type</p>
  <Search data={employmentType} setData={store.setEmploymentType} />
  <Spacer axis="y" size="24" />
  <div class="flex gap-8px items-center">
    <input
      onchange={store.toggleIncludeRemoteJobs}
      value={store.includeRemoteJobs}
      type="checkbox"
      id="remote-checkbox"
    />
    <label for="remote-checkbox">Include remote jobs</label>
  </div>
  <Spacer axis="y" size="8" />
  <div class="flex gap-8px items-center">
    <input
      onchange={store.toggleIncludeUSCitizenJobsOnly}
      value={store.includeUSCitizenJobsOnly}
      type="checkbox"
      id="citizen-checkbox"
    />
    <label for="citizen-checkbox">Include US citizen jobs only</label>
  </div>
  <Spacer axis="y" size="24" />
  <button
    class="bg-black text-white rounded-4px px-12px py-4px flex gap-12px items-center"
    onclick={async () => {
      isLoading = true;
      await store.getJobListings(true);
      isLoading = false;
    }}
    disabled={isLoading}
  >
    {#if isLoading}
      Loading
      <div
        class="border-t-[white] border-l-[white] border-b-[white]
        w-[16px] h-[16px] border-[2px] border-transparent spinner animate-spin rounded-circle"
      ></div>
    {:else}
      Search
    {/if}
  </button>
</div>
