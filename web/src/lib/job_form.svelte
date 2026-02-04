<script lang="ts">
  import Search from "$lib/multiselect.svelte";
  import Spacer from "./spacer.svelte";
  import { stateAbbreviations } from "../utils";

  const {
    getJobListings,
    setDegreeRequirements,
    setLocations,
    setEmploymentType,
    setFile,
    toggleIncludeRemoteJobs,
    toggleIncludeUSCitizenJobsOnly,
  } = $props();

  let isLoading = $state(false);
  const degreeRequirements = ["No degree", "Required"];

  const employmentType = ["Part-time", "Full-time", "Contract", "Internship"];
</script>

<div
  class="bg-white max-[600px]:mb-10 [border:1px_solid_#E6E6E6]
  max-[600px]:w-full max-[600px]:max-w-[600px] max-w-[400px] w-[45vw] rounded-8px 
  max-[600px]:relative sticky max[600-px]:top-12px top-24px px-20px py-32px"
>
  <p>
    <span class="font-600">Interview Moves</span> matches your resume with job openings
    in the IT field.
  </p>
  <Spacer axis="y" size="24" />
  <p class="font-600">Upload resume</p>
  <input
    class="mt-1 [border:1px_solid_#DADADA] rounded-md px-12px py-2 w-full"
    type="file"
    onchange={(e) => setFile((e.target as HTMLInputElement).files?.[0] ?? "")}
  />
  <Spacer axis="y" size="24" />
  <p class="font-600">Locations</p>
  <Search
    data={["All", ...Object.keys(stateAbbreviations)]}
    setData={setLocations}
  />
  <Spacer axis="y" size="24" />
  <p class="font-600">Degree requirements</p>
  <Search data={degreeRequirements} setData={setDegreeRequirements} />
  <Spacer axis="y" size="24" />
  <p class="font-600">Employment type</p>
  <Search data={employmentType} setData={setEmploymentType} />
  <Spacer axis="y" size="24" />
  <div class="flex gap-8px items-center">
    <input
      onchange={toggleIncludeRemoteJobs}
      type="checkbox"
      id="remote-checkbox"
    />
    <label for="remote-checkbox">Include remote jobs</label>
  </div>
  <Spacer axis="y" size="8" />
  <div class="flex gap-8px items-center">
    <input
      onchange={toggleIncludeUSCitizenJobsOnly}
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
      await getJobListings(true);
      isLoading = false;
    }}
    disabled={isLoading}
  >
    {#if isLoading}
      Loading
      <div
        class="border-t-[white] border-l-[white] border-b-[white] w-[16px]
        h-[16px] border-[2px] border-transparent spinner animate-spin rounded-circle"
      ></div>
    {:else}
      Search
    {/if}
  </button>
</div>
